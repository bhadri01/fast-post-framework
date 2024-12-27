from pydantic import BaseModel, create_model
from sqlalchemy import inspect
from datetime import datetime, timezone, timedelta
from typing import Optional

# Define IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

def generate_schemas(model):
    # Inspect SQLAlchemy model columns
    mapper = inspect(model)
    fields = {
        column.key: (Optional[column.type.python_type], None) if column.nullable else (column.type.python_type, ...)
        for column in mapper.columns
    }

    # Exclude fields for the Create and Update schemas
    exclude_fields = ["id", "documentId", "createdAt", "updatedAt", "createdBy", "updatedBy"]
    
    create_fields = {
        key: value
        for key, value in fields.items()
        if key not in exclude_fields
    }

    update_fields = {
        key: (Optional[value[0]], None)
        for key, value in fields.items()
        if key not in exclude_fields
    }

    # Dynamically create Pydantic models
    SchemaCreate = create_model(f"{model.__name__}Create", **create_fields)
    SchemaUpdate = create_model(f"{model.__name__}Update", **update_fields)  # Allow all fields for updates

    # Define a custom Response schema with default fields
    class BaseResponse(BaseModel):
        id: int
        documentId: Optional[str] = None
        createdAt: datetime
        updatedAt: datetime
        createdBy: Optional[str] = None
        updatedBy: Optional[str] = None

        class Config:
            from_attributes = True
            json_encoders = {
                datetime: lambda v: v.astimezone(IST).isoformat(),
            }

    SchemaResponse = create_model(
        f"{model.__name__}Response", 
        __base__=BaseResponse,
        **fields,  # Add model-specific fields
    )

    return SchemaCreate, SchemaUpdate, SchemaResponse