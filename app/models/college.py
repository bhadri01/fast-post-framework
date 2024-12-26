from sqlalchemy import Column, String, Integer
from app.core.database import Base

class College(Base):
    __tablename__ = "colleges"

    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    established_year = Column(Integer, nullable=True)
    contact_email = Column(String, nullable=False)
