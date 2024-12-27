from app.generator.base import create_crud_routes
from typing import List, Callable, Dict, Type, Tuple
from app.models.user import UserRole
from fastapi import APIRouter
from pydantic import BaseModel


def generate_crud_router(
    model: Type,
    schemas: Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel]],
    required_roles: Dict[str, List[UserRole]] = None,
    custom_routes: List[Callable[[APIRouter], None]] = None
) -> APIRouter:
    schema_create, schema_update, schema_response = schemas
    return create_crud_routes(
        model=model,
        schema_create=schema_create,
        schema_update=schema_update,
        schema_response=schema_response,
        tags=[model.__name__.capitalize()],
        required_roles=required_roles,
        custom_routes=custom_routes
    )
