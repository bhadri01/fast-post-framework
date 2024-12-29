from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    
    name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="role")

    def __init__(self, name):
        self.name = name.lower()
