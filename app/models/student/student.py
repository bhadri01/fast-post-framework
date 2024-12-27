from sqlalchemy import Column, String, DateTime
from app.core.database import Base


class Student(Base):
    __tablename__ = 'students'

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
