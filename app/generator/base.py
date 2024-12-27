from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import Page, add_pagination
from app.core.database import get_read_session, get_write_session
from typing import Type, Optional, Dict, List, Callable
from app.services.filtering import parse_filters
from app.models.user import UserRole
from sqlalchemy.future import select
from sqlalchemy import asc, desc
from fastapi_pagination.ext.sqlalchemy import paginate
import json

def create_crud_routes(
    model: Type,
    schema_create: Type,
    schema_update: Type,
    schema_response: Type,
    tags: Optional[list] = None,
    required_roles: Optional[Dict[str, List[UserRole]]] = None,
    custom_routes: Optional[List[Callable[[APIRouter], None]]] = None,
) -> APIRouter:
    router = APIRouter(tags=tags or [model.__name__.capitalize()])

    def parse_filter_query(filters: Optional[str]) -> Optional[dict]:
        if filters:
            try:
                return json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400, detail="Invalid filter JSON")
        return None
    
    # Add custom routes if provided
    if custom_routes:
        for custom_route in custom_routes:
            custom_route(router)

    @router.get("", response_model=Page[schema_response])
    async def read_all(
        filters: Optional[str] = Query(None),
        sort: Optional[str] = Query(None),
        session: AsyncSession = Depends(get_read_session)
    ):
        try:
            parsed_filters = parse_filter_query(filters)
            filter_expression = parse_filters(model, parsed_filters) if parsed_filters else None
            query = select(model)
            if filter_expression is not None:
                query = query.where(filter_expression)
            if sort:
                try:
                    sort_field, sort_direction = sort.split(":")
                    if sort_direction.lower() not in ["asc", "desc"]:
                        raise HTTPException(
                            status_code=400, detail="Invalid sort direction. Use 'asc' or 'desc'.")
                    column = getattr(model, sort_field, None)
                    if column is None:
                        raise ValueError(f"Invalid sort field: {sort_field}")
                    query = query.order_by(
                        asc(column) if sort_direction.lower() == "asc" else desc(column))
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
            else:
                query = query.order_by(asc(model.id))

            result = await paginate(session, query)
            return result
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{id}", response_model=schema_response)
    async def read_one(id: int, session: AsyncSession = Depends(get_read_session)):
        try:
            db_data = await session.execute(select(model).where(model.id == id))
            db_data = db_data.scalar_one_or_none()
            if not db_data:
                raise Exception("Data not found")
            return db_data
        except ValueError:
            raise HTTPException(status_code=400, detail="ID must be a valid integer.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("", response_model=schema_response)
    async def create(item: schema_create, session: AsyncSession = Depends(get_write_session)):
        try:
            obj = model(**item.dict())
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.put("/{id}", response_model=schema_response)
    async def update(id: int, item: schema_update, session: AsyncSession = Depends(get_write_session)):
        try:
            db_data = await session.execute(select(model).where(model.id == id))
            db_data = db_data.scalar_one_or_none()
            if not db_data:
                raise Exception("Data not found")
            try:
                update_data = item.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    if hasattr(db_data, key):
                        setattr(db_data, key, value)
                await session.commit()
                await session.refresh(db_data)
                return db_data
            except Exception as e:
                await session.rollback()
                raise HTTPException(
                    status_code=400,
                    detail={"message":  "Failed to update record",
                            "error": str(e)},
                )
        except ValueError:
            raise HTTPException(status_code=400, detail="ID must be a valid integer.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.delete("/{id}", response_model=bool)
    async def delete(id: int, session: AsyncSession = Depends(get_write_session)):
        try:
            db_data = await session.execute(select(model).where(model.id == id))
            db_data = db_data.scalar_one_or_none()
            if not db_data:
                raise Exception("Data not found")
            await session.delete(db_data)
            await session.commit()
            return True
        except ValueError:
            raise HTTPException(status_code=400, detail="ID must be a valid integer.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    

    add_pagination(router)
    return router