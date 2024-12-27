from sqlalchemy import Column, String, Integer,ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    # Establish reverse relationship
    users = relationship("User", back_populates="role")

