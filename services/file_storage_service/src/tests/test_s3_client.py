"""
Unit tests for app.s3_client.py
Covers bucket creation, S3 errors, and the async generator.
"""
from unittest.mock import AsyncMock

import pytest
from botocore.exceptions import ClientError

from app.s3_client import create_bucket_if_not_exists, get_s3_client


@pytest.mark.asyncio
async def test_get_s3_client_async_generator():
    # Consume the async generator correctly
    async for client in get_s3_client():
        assert client is not None


@pytest.mark.asyncio
async def test_create_bucket_if_not_exists_existing_bucket(monkeypatch):
    mock_client = AsyncMock()
    # head_bucket succeeds (bucket exists)
    async def fake_get_client():
        yield mock_client
    monkeypatch.setattr("app.s3_client.get_s3_client", fake_get_client)

    await create_bucket_if_not_exists()
    mock_client.head_bucket.assert_called_once()


@pytest.mark.asyncio
async def test_create_bucket_if_not_exists_bucket_missing(monkeypatch):
    mock_client = AsyncMock()
    # head_bucket raises 404
    async def head_bucket(Bucket):
        raise ClientError({"Error": {"Code": "404", "Message": "Not Found"}}, "HeadBucket")
    mock_client.head_bucket.side_effect = head_bucket

    async def fake_get_client():
        yield mock_client
    monkeypatch.setattr("app.s3_client.get_s3_client", fake_get_client)

    await create_bucket_if_not_exists()
    mock_client.create_bucket.assert_called_once()


@pytest.mark.asyncio
async def test_create_bucket_if_not_exists_unexpected_error(monkeypatch):
    mock_client = AsyncMock()
    # head_bucket raises unknown error
    async def head_bucket(Bucket):
        raise ClientError({"Error": {"Code": "500", "Message": "Internal Error"}}, "HeadBucket")
    mock_client.head_bucket.side_effect = head_bucket

    async def fake_get_client():
        yield mock_client
    monkeypatch.setattr("app.s3_client.get_s3_client", fake_get_client)

    with pytest.raises(ClientError):
        await create_bucket_if_not_exists()
