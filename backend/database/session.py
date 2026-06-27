"""Async database session helpers."""

from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def create_session_factory(database_url: str) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory for the configured database URL."""

    engine = create_async_engine(database_url, echo=False, future=True)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    """Yield an async SQLAlchemy session.

    This helper is compatible with FastAPI dependencies and background workers.
    """

    async with session_factory() as session:
        yield session
