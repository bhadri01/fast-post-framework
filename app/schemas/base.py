from datetime import datetime, timezone, timedelta
from pydantic import BaseModel

# Define IST timezone
IST = timezone(timedelta(hours=5, minutes=30))

class Response(BaseModel):
    id: int
    documentId: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            # Convert to IST and format as ISO8601
            datetime: lambda v: v.astimezone(IST).isoformat()
        }