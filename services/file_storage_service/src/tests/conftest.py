from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app
from app.s3_client import get_s3_client


@pytest.fixture(scope='session', autouse=True)
def override_settings():
    """Fixture to override app settings for all tests."""
    # Define settings with distinct internal and public URLs for robust testing
    test_settings = Settings(
        APP_TITLE='Test File Storage Service',
        S3_ENDPOINT_URL='http://internal-s3:9000',
        S3_PUBLIC_URL='http://public-s3.example.com',
        MINIO_ROOT_USER='testuser',
        MINIO_ROOT_PASSWORD='testpassword',
        MINIO_BUCKET_NAME='test-bucket',
    )
    # Monkey patch the settings object in the app's config module
    import app.core.config

    app.core.config.settings = test_settings


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def mock_s3_client():
    """Mock S3 client for unit testing."""
    mock_client = AsyncMock()
    mock_client.upload_fileobj = AsyncMock()
    mock_client.head_object = AsyncMock()
    mock_client.head_bucket = AsyncMock()
    mock_client.create_bucket = AsyncMock()
    mock_client.generate_presigned_url = AsyncMock()
    return mock_client


@pytest.fixture
def override_s3_client(mock_s3_client):
    """
    Fixture to override the S3 client dependency with a mock for unit tests.
    This ensures no real network calls are made.
    """

    async def get_mock_s3_client():
        yield mock_s3_client

    app.dependency_overrides[get_s3_client] = get_mock_s3_client
    yield mock_s3_client
    # Clean up the override after the test is done
    app.dependency_overrides.clear()
