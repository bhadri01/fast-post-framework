from sqlalchemy import Column, String, ForeignKey, event,Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.utils.security import get_password_hash


class User(Base):
    __tablename__ = "users"

    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_block = Column(Boolean, default=False, nullable=False)
    role_id = Column(String(24), ForeignKey("roles.documentId"), nullable=False)
    role = relationship("Role", back_populates="users", lazy="joined")

@event.listens_for(User, "before_insert")
def hash_user_password(mapper, connection, target):
    if target.password:
        target.password = get_password_hash(target.password)

@event.listens_for(User, "before_update")
def hash_user_password(mapper, connection, target):
    if target.password:
        target.password = get_password_hash(target.password)