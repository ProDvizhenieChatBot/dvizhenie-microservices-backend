"""
Pytest configuration and fixtures for API Service tests.

This module provides shared fixtures for testing, including:
- Async test database setup
- Mock data factories
- Test client configuration
"""

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import cast

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base, get_async_session
from app.main import app
from app.models import db_models  # noqa: F401
from app.models.db_models import Application, ApplicationFile, FormSchema


TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """Creates and drops the database for each test function."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_database: None) -> AsyncGenerator[AsyncSession, None]:
    """Provides a clean database session for each test."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def test_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provides an async HTTP client for testing API endpoints."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_form_schema() -> dict:
    """Returns a minimal form schema for testing."""
    return {
        'name': 'Test Form',
        'version': '1.0',
        'start_step_id': 'step1',
        'steps': [
            {
                'step_id': 'step1',
                'title': 'Test Step',
                'fields': [
                    {
                        'field_id': 'test_field',
                        'type': 'text',
                        'label': 'Test Field',
                        'required': True,
                    }
                ],
                'navigation': {'type': 'direct', 'next_step_id': 'step2'},
            }
        ],
    }


@pytest.fixture
async def active_form_schema(
    db_session: AsyncSession, sample_form_schema: dict
) -> AsyncGenerator[FormSchema, None]:
    """Creates and returns an active form schema in the database."""
    schema = FormSchema(version='1.0', schema_data=sample_form_schema, is_active=True)
    db_session.add(schema)
    await db_session.commit()
    await db_session.refresh(schema)
    return cast(FormSchema, schema)


@pytest.fixture
async def draft_application(db_session: AsyncSession) -> AsyncGenerator[Application, None]:
    """Creates and returns a draft application."""
    app_data = Application(
        id=uuid.uuid4(),
        telegram_id=123456789,
        status='draft',
        data={'test_field': 'test_value'},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(app_data)
    await db_session.commit()
    await db_session.refresh(app_data)
    return cast(Application, app_data)


@pytest.fixture
async def submitted_application(db_session: AsyncSession) -> AsyncGenerator[Application, None]:
    """Creates and returns a submitted application."""
    app_data = Application(
        id=uuid.uuid4(),
        telegram_id=987654321,
        status='new',
        data={'name': 'John Doe', 'email': 'john@example.com'},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(app_data)
    await db_session.commit()
    await db_session.refresh(app_data)
    return cast(Application, app_data)


@pytest.fixture
async def application_with_files(
    db_session: AsyncSession, draft_application: Application
) -> AsyncGenerator[Application, None]:
    """Creates an application with linked files."""
    file1 = ApplicationFile(
        application_id=draft_application.id,
        file_id='file1.pdf',
        original_filename='document1.pdf',
        form_field_id='passport_scan',
    )
    file2 = ApplicationFile(
        application_id=draft_application.id,
        file_id='file2.jpg',
        original_filename='photo.jpg',
        form_field_id='beneficiary_photo',
    )

    db_session.add_all([file1, file2])
    await db_session.commit()
    await db_session.refresh(draft_application)
    return cast(Application, draft_application)
