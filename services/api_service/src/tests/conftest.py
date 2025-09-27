# services/api_service/src/tests/conftest.py
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.main import app


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture to get an async database session for tests.
    """
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that provides an HTTPX client for making requests to the test app.
    """
    # The 'app' argument is functionally correct, but its type hints are
    # not perfectly compatible with httpx's expectations. We ignore the error.
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test',  # type: ignore
    ) as ac:
        yield ac
