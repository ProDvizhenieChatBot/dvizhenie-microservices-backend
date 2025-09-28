from unittest.mock import AsyncMock, patch

import pytest

from app.main import app, lifespan


@pytest.mark.unit
def test_health_check_endpoint(client):
    """Test the health check endpoint returns the correct status."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'service': 'File Storage Service'}


@pytest.mark.asyncio
@pytest.mark.unit
async def test_lifespan_startup_event():
    """Test that the lifespan manager calls the bucket creation logic on startup."""
    with patch(
        'app.main.create_bucket_if_not_exists', new_callable=AsyncMock
    ) as mock_create_bucket:
        # Simulate the application startup-shutdown cycle
        async with lifespan(app):
            pass  # Startup logic runs here

        mock_create_bucket.assert_called_once()
