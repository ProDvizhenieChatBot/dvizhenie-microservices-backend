from unittest.mock import AsyncMock, patch

import pytest
from botocore.exceptions import ClientError

from app.s3_client import create_bucket_if_not_exists, get_s3_client


@pytest.mark.asyncio
@pytest.mark.unit
async def test_get_s3_client_context_manager():
    """Test that the get_s3_client dependency yields a client."""
    with patch('app.s3_client.session.client') as mock_session_client:
        mock_client = AsyncMock()
        # Mock the async context manager (__aenter__)
        mock_session_client.return_value.__aenter__.return_value = mock_client

        async for client in get_s3_client():
            assert client == mock_client
            break  # Exit after one iteration


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_bucket_if_not_exists_when_bucket_already_exists():
    """Test that the bucket is not created if it already exists."""
    with patch('app.s3_client.get_s3_client') as mock_get_client:
        mock_client = AsyncMock()
        # Make the async generator yield our mock client
        mock_get_client.return_value.__aiter__ = AsyncMock(return_value=iter([mock_client]))

        # Mock that the bucket exists (head_bucket does not raise an error)
        mock_client.head_bucket.return_value = None

        await create_bucket_if_not_exists()

        mock_client.head_bucket.assert_called_once_with(Bucket='test-bucket')
        mock_client.create_bucket.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_bucket_if_not_exists_when_bucket_is_new():
    """Test that a new bucket is created if it does not exist."""
    with patch('app.s3_client.get_s3_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value.__aiter__ = AsyncMock(return_value=iter([mock_client]))

        # Mock a '404 Not Found' error to simulate the bucket not existing
        error_response = {'Error': {'Code': '404'}}
        mock_client.head_bucket.side_effect = ClientError(error_response, 'HeadBucket')
        mock_client.create_bucket.return_value = None

        await create_bucket_if_not_exists()

        mock_client.head_bucket.assert_called_once_with(Bucket='test-bucket')
        mock_client.create_bucket.assert_called_once_with(Bucket='test-bucket')


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_bucket_raises_error_on_creation_failure():
    """Test that an exception is raised if creating the bucket fails."""
    with patch('app.s3_client.get_s3_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value.__aiter__ = AsyncMock(return_value=iter([mock_client]))

        # Mock bucket not found
        error_404 = {'Error': {'Code': '404'}}
        mock_client.head_bucket.side_effect = ClientError(error_404, 'HeadBucket')

        # Mock a different error on create_bucket (e.g., 'Access Denied')
        create_error = {'Error': {'Code': '403', 'Message': 'Access Denied'}}
        mock_client.create_bucket.side_effect = ClientError(create_error, 'CreateBucket')

        with pytest.raises(ClientError):
            await create_bucket_if_not_exists()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_bucket_raises_unexpected_head_error():
    """Test that unexpected errors from head_bucket are raised."""
    with patch('app.s3_client.get_s3_client') as mock_get_client:
        mock_client = AsyncMock()
        mock_get_client.return_value.__aiter__ = AsyncMock(return_value=iter([mock_client]))

        # Mock a non-404 error from head_bucket
        error_response = {'Error': {'Code': '500', 'Message': 'Server Error'}}
        mock_client.head_bucket.side_effect = ClientError(error_response, 'HeadBucket')

        with pytest.raises(ClientError):
            await create_bucket_if_not_exists()
