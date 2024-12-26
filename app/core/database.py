from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from fastapi import Request
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import as_declarative
import uuid

Base = declarative_base()


@as_declarative()
class Base:
    """
    Base model to include default columns for all tables.
    """
    id = Column(Integer, primary_key=True, index=True)
    documentId = Column(String(24), nullable=False,
                        default=lambda: str(uuid.uuid4().hex)[:24])
    createdAt = Column(DateTime, nullable=False, server_default=func.now())
    updatedAt = Column(DateTime, nullable=False,
                       server_default=func.now(), onupdate=func.now())
    createdBy = Column(String, nullable=True)  # Track the creator
    updatedBy = Column(String, nullable=True)  # Track the updater


def create_engine(url, **kwargs):
    """Create an asynchronous SQLAlchemy engine."""
    return create_async_engine(url, echo=False, **kwargs)


master_db_engine = create_engine(settings.postgresql_database_master_url)
slave_db_engine = create_engine(
    settings.postgresql_database_slave_url,
    pool_size=20, max_overflow=10, pool_recycle=3600,pool_timeout=30, pool_pre_ping=True
)

# Async session factories
async_master_session = async_sessionmaker(
    bind=master_db_engine, autocommit=False, autoflush=False)
async_slave_session = async_sessionmaker(
    bind=slave_db_engine, autocommit=False, autoflush=False)


async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide a database session.
    """
    async with async_master_session() as session:
        yield session


async def get_read_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide a database session.
    """
    async with async_slave_session() as session:
        yield session
