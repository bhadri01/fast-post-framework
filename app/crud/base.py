from typing import Type, TypeVar, Generic, List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_pagination import Page
from pydantic import BaseModel
from sqlalchemy import asc, desc

# Type variables for the generic CRUD class
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_all(self, session: AsyncSession, filters: Optional[Any] = None, sort: Optional[tuple] = None) -> Page[ModelType]:
        query = select(self.model)
        # Apply filters if provided
        if filters is not None:
            query = query.where(filters)
        # Apply sorting if provided
        if sort:
            sort_field, sort_direction = sort
            column = getattr(self.model, sort_field, None)
            if column is None:
                raise ValueError(f"Invalid sort field: {sort_field}")
            query = query.order_by(
                asc(column) if sort_direction.lower() == "asc" else desc(column))
        else:
            # Default sorting by id in ascending order
            query = query.order_by(asc(self.model.id))

        return await paginate(session, query)

    async def get(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """
        Retrieve a single record by ID.
        """
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def create(self, session: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        """
        obj = self.model(**obj_in.dict())
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def update(
        self, session: AsyncSession, id: int, obj_in: UpdateSchemaType
    ) -> Dict[str, Any]:
        """
        Update an existing record by ID with dynamic field updates.
        """
        try:
            # Get the existing record
            db_obj = await self.get(session, id)
            if not db_obj:
                return {"success": False, "message": "Record not found"}

            # Dynamically update fields
            update_data = obj_in.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)

            # Commit changes
            await session.commit()
            await session.refresh(db_obj)

            return {"success": True, "data": db_obj, "message": "Record updated successfully"}

        except Exception as e:
            await session.rollback()
            return {"success": False, "message": "Failed to update record", "error": str(e)}

    async def delete(self, session: AsyncSession, id: int) -> bool:
        """
        Delete a record by ID.
        """
        db_obj = await self.get(session, id)
        if not db_obj:
            return False

        await session.delete(db_obj)
        await session.commit()
        return True
