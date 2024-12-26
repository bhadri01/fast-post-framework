from pydantic import BaseModel
from typing import Optional
from app.schemas.base import Response


class CollegeBase(BaseModel):
    name: str
    contact_email: str
    location: Optional[str] = None
    established_year: Optional[int] = None


class CollegeCreate(CollegeBase):
    pass


class CollegeUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    established_year: Optional[int] = None
    contact_email: Optional[str] = None


class CollegeResponse(Response, CollegeBase):
    pass
