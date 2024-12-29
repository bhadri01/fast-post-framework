from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_read_session,get_write_session
from typing import Type, Optional, Dict, List, Callable
from app.services.filtering import parse_filters
from sqlalchemy.future import select
from sqlalchemy import asc, desc, func
from sqlalchemy.exc import SQLAlchemyError
import json
from app.utils.security import get_current_active_user_with_roles
from math import ceil


def create_crud_routes(
    model: Type,
    schema_create: Type,
    schema_update: Type,
    schema_response: Type,
    tags: Optional[list] = None,
    required_roles: Optional[Dict[str, List[str]]] = None,
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

    def select_fields(query, fields: Optional[str]):
        if fields:
            try:
                selected_fields = [getattr(model, field.strip())
                                   for field in fields.split(",") if hasattr(model, field.strip())]
                if not selected_fields:
                    raise HTTPException(
                        status_code=400, detail="Invalid fields specified.")
                # Use * to unpack the selected fields into positional arguments
                query = query.with_only_columns(*selected_fields)
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        return query

    # Add custom routes if provided
    if custom_routes:
        for custom_route in custom_routes:
            custom_route(router)

    @router.get("")
    async def read_all(
        filters: Optional[str] = Query(None),
        sort: Optional[str] = Query(None),
        fields: Optional[str] = Query(
            None, description="Comma-separated list of fields to include in the response"),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(50, ge=1, le=100, description="Page size"),
        session: AsyncSession = Depends(get_read_session),
        current_user=Depends(get_current_active_user_with_roles(
            required_roles.get("read_all", []))),
    ):
        try:
            parsed_filters = parse_filter_query(filters)
            filter_expression = parse_filters(
                model, parsed_filters) if parsed_filters else None

            # Start with base query
            query = select(model)

            if filter_expression is not None:
                query = query.where(filter_expression)

            if sort:
                try:
                    sort_field, sort_direction = sort.split(":")
                    if sort_direction.lower() not in ["asc", "desc"]:
                        raise HTTPException(
                            status_code=400, detail="Invalid sort direction. Use 'asc' or 'desc'."
                        )
                    column = getattr(model, sort_field, None)
                    if column is None:
                        raise ValueError(f"Invalid sort field: {sort_field}")
                    query = query.order_by(
                        asc(column) if sort_direction.lower(
                        ) == "asc" else desc(column)
                    )
                except ValueError as e:
                    raise HTTPException(status_code=400, detail=str(e))
            else:
                query = query.order_by(asc(model.createdAt))

            # Handle fields selection
            if fields:
                selected_fields = [getattr(model, field.strip()) for field in fields.split(
                    ",") if hasattr(model, field.strip())]
                if not selected_fields:
                    raise HTTPException(
                        status_code=400, detail="Invalid fields specified.")
                query = query.with_only_columns(*selected_fields)

            # Count total records for pagination
            total_query = select(func.count()).select_from(query.subquery())
            total_result = await session.execute(total_query)
            total_records = total_result.scalar()

            # Apply pagination
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)

            # Execute the query
            result = await session.execute(query)
            rows = result.fetchall()

            # Convert rows to dictionaries using _mapping
            response = [dict(row._mapping) for row in rows]

            # Remove the outer key
            if response and isinstance(response[0], dict) and len(response[0]) == 1:
                response = [list(item.values())[0] for item in response]

            # Create paginated response
            total_pages = ceil(total_records / size)
            return {
                "data": response,
                "meta": {
                    "total_records": total_records,
                    "total_pages": total_pages,
                    "current_page": page,
                    "page_size": size,
                },
            }
        except SQLAlchemyError as e:
            error_message = str(e).split("\n")[1]
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/{documentId}")
    async def read_one(
        documentId: str,
        fields: Optional[str] = Query(
            None, description="Comma-separated list of fields to include in the response"),
        session: AsyncSession = Depends(get_read_session),
        current_user=Depends(get_current_active_user_with_roles(
            required_roles.get("read_one", [])))
    ):
        try:
            # Base query
            query = select(model).where(model.documentId == documentId)

            # Handle fields selection
            if fields:
                selected_fields = [getattr(model, field.strip()) for field in fields.split(
                    ",") if hasattr(model, field.strip())]
                if not selected_fields:
                    raise HTTPException(
                        status_code=400, detail="Invalid fields specified.")
                query = query.with_only_columns(*selected_fields)

            # Execute the query
            result = await session.execute(query)
            db_data = result.fetchone()  # Fetch a single row

            # Check if data exists
            if not db_data:
                raise HTTPException(status_code=404, detail="Data not found")

            # Convert to dictionary
            return dict(db_data._mapping)
        except SQLAlchemyError as e:
            error_message = str(e).split("\n")[1]
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("")
    async def create(item: schema_create, session: AsyncSession = Depends(get_write_session),
                     current_user=Depends(get_current_active_user_with_roles(
                         required_roles.get("create", [])))):
        try:
            obj = model(**item.dict())
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            error_message = str(e).split("\n")
            raise HTTPException(status_code=400, detail=error_message)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.put("/{documentId}")
    async def update(documentId: str, item: schema_update, session: AsyncSession = Depends(get_write_session),
                     current_user=Depends(get_current_active_user_with_roles(
                         required_roles.get("update", [])))):
        try:
            db_data = await session.execute(select(model).where(model.documentId == documentId))
            db_data = db_data.scalar_one_or_none()
            if not db_data:
                raise Exception("Data not found")
            update_data = item.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(db_data, key):
                    setattr(db_data, key, value)
            await session.commit()
            await session.refresh(db_data)
            return db_data
        except SQLAlchemyError as e:
            error_message = str(e).split("\n")[1]
            raise HTTPException(status_code=400, detail=error_message)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="ID must be a valid integer.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.delete("/{documentId}", response_model=bool)
    async def delete(documentId: str, session: AsyncSession = Depends(get_write_session), current_user=Depends(get_current_active_user_with_roles(
            required_roles.get("delete", [])))):
        try:
            db_data = await session.execute(select(model).where(model.documentId == documentId))
            db_data = db_data.scalar_one_or_none()
            if not db_data:
                raise Exception("Data not found")
            await session.delete(db_data)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            error_message = str(e).split("\n")[1]
            raise HTTPException(status_code=400, detail=error_message)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="ID must be a valid integer.")
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return router
