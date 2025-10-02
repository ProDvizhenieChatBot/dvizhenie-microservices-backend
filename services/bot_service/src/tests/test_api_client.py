"""
Unit tests for the ApiClient.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import HTTPStatusError, Request, Response

from app.internal_clients.api_client import ApiClient


BASE_URL = 'http://test-api'


@pytest.fixture
def api_client() -> ApiClient:
    """Provides an ApiClient instance with a test URL."""
    return ApiClient(base_url=BASE_URL)


@pytest.mark.asyncio
@patch('app.internal_clients.api_client.httpx.AsyncClient')
async def test_create_telegram_session_success(mock_async_client_cls, api_client: ApiClient):
    """Test successful session creation returns application UUID."""
    mock_client = mock_async_client_cls.return_value.__aenter__.return_value
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    # FIX: .json() is a sync method, so it should be a MagicMock
    mock_response.json = MagicMock(return_value={'application_uuid': 'test-uuid-123'})
    mock_client.post.return_value = mock_response

    result = await api_client.create_telegram_session(telegram_id=123)

    assert result == 'test-uuid-123'
    mock_client.post.assert_awaited_once_with(
        f'{BASE_URL}/api/v1/sessions/telegram', json={'telegram_id': 123}
    )


@pytest.mark.asyncio
@patch('app.internal_clients.api_client.httpx.AsyncClient')
async def test_create_telegram_session_http_error(mock_async_client_cls, api_client: ApiClient):
    """Test that HTTP errors during session creation return None."""
    mock_client = mock_async_client_cls.return_value.__aenter__.return_value
    mock_client.post.side_effect = HTTPStatusError(
        'Server Error',
        request=Request('POST', BASE_URL),
        response=Response(500),
    )

    result = await api_client.create_telegram_session(telegram_id=123)

    assert result is None


@pytest.mark.asyncio
@patch('app.internal_clients.api_client.httpx.AsyncClient')
async def test_get_status_success(mock_async_client_cls, api_client: ApiClient):
    """Test successful status retrieval returns the status string."""
    mock_client = mock_async_client_cls.return_value.__aenter__.return_value
    mock_response = AsyncMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.status_code = 200
    # FIX: .json() is a sync method, so it should be a MagicMock
    mock_response.json = MagicMock(return_value={'status': 'in_progress'})
    mock_client.get.return_value = mock_response

    result = await api_client.get_telegram_application_status(telegram_id=123)

    assert result == 'in_progress'
    mock_client.get.assert_awaited_once_with(
        f'{BASE_URL}/api/v1/sessions/telegram/status', params={'telegram_id': 123}
    )


@pytest.mark.asyncio
@patch('app.internal_clients.api_client.httpx.AsyncClient')
async def test_get_status_not_found(mock_async_client_cls, api_client: ApiClient):
    """Test that a 404 status returns 'not_found'."""
    mock_client = mock_async_client_cls.return_value.__aenter__.return_value
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_client.get.return_value = mock_response

    result = await api_client.get_telegram_application_status(telegram_id=123)

    assert result == 'not_found'


@pytest.mark.asyncio
@patch('app.internal_clients.api_client.httpx.AsyncClient')
async def test_get_status_http_error(mock_async_client_cls, api_client: ApiClient):
    """Test that other HTTP errors during status retrieval return None."""
    mock_client = mock_async_client_cls.return_value.__aenter__.return_value
    mock_client.get.side_effect = HTTPStatusError(
        'Server Error',
        request=Request('GET', BASE_URL),
        response=Response(500),
    )

    result = await api_client.get_telegram_application_status(telegram_id=123)

    assert result is None
