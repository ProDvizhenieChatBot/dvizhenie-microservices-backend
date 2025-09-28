# services/api_service/src/tests/conftest.py
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal, get_async_session
from app.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to get an async database session for tests.
    """
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that provides an HTTPX client for making requests to the test app.
    Overrides the database dependency to use the same session as the test.
    """

    # Override the database dependency to use our test session
    async def override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test',  # type: ignore
        ) as ac:
            yield ac
    finally:
        # Clean up the override after the test
        app.dependency_overrides.clear()
