"""
Pytest configuration and fixtures for File Storage Service tests.
"""
import io
import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app


# --------------------------
# Set dummy AWS credentials
# --------------------------
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

# --------------------------
# Override settings
# --------------------------
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    monkeypatch.setattr('app.core.config.settings.S3_ENDPOINT_URL', 'http://localhost:9000')
    monkeypatch.setattr('app.core.config.settings.S3_PUBLIC_URL', 'http://public-s3')
    monkeypatch.setattr('app.core.config.settings.MINIO_BUCKET_NAME', 'test-bucket')


# --------------------------
# Mocked async S3 client
# --------------------------
@pytest.fixture
def s3_client() -> AsyncGenerator:
    """
    Provides a mocked S3 client with internal storage for uploaded files.
    """
    client = AsyncMock()
    storage = {}

    async def async_upload_fileobj(Fileobj, Bucket, Key):
        content = Fileobj.read() if hasattr(Fileobj, "read") else Fileobj
        storage[Key] = content
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    async def async_head_object(Bucket, Key):
        if Key not in storage:
            from botocore.exceptions import ClientError
            raise ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}},
                "HeadObject"
            )
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    async def async_get_object(Bucket, Key):
        if Key not in storage:
            from botocore.exceptions import ClientError
            raise ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}},
                "GetObject"
            )
        return {"Body": io.BytesIO(storage[Key])}

    def generate_presigned_url(ClientMethod, Params, ExpiresIn):
        return f"{settings.S3_PUBLIC_URL}/{Params['Key']}?X-Amz-Test"

    client.upload_fileobj.side_effect = async_upload_fileobj
    client.head_object.side_effect = async_head_object
    client.get_object.side_effect = async_get_object
    client.generate_presigned_url.side_effect = generate_presigned_url

    return client


# --------------------------
# Async test HTTP client
# --------------------------
@pytest.fixture
async def test_client(s3_client) -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an async HTTP client for testing API endpoints.
    Overrides the `get_s3_client` dependency to inject the mocked S3 client.
    """
    from app.s3_client import get_s3_client

    async def override_get_s3() -> AsyncGenerator:
        yield s3_client

    app.dependency_overrides[get_s3_client] = override_get_s3

    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        yield client

    app.dependency_overrides.clear()
