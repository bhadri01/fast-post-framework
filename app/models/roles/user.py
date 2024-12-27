from sqlalchemy import Column, String, Integer,ForeignKey,event
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.utils.security import hash_password


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False,)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)  # Use string reference for "roles.id"

    # Use lazy='joined' for eager loading
    role = relationship("Role", back_populates="users", lazy="joined")

@event.listens_for(User, "before_insert")
def hash_user_password(mapper, connection, target):
    if target.hashed_password:
        target.hashed_password = hash_password(target.hashed_password)

# Event listener to hash password before update
@event.listens_for(User, "before_update")
def hash_user_password(mapper, connection, target):
    if target.hashed_password:
        target.hashed_password = hash_password(target.hashed_password)
