# services/api_service/src/tests/test_applications.py
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Application


pytestmark = pytest.mark.asyncio


class TestApplicationCreation:
    """
    Tests for the application creation lifecycle.
    """

    async def test_create_draft_application_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        """
        Tests that a POST request to /api/v1/applications/ successfully creates
        a draft application and returns a 201 status code.
        """
        response = await client.post('/api/v1/applications/', json={})

        assert response.status_code == 201

        data = response.json()
        assert 'id' in data
        assert data['status'] == 'draft'
        new_app_id = data['id']

        stmt = select(Application).where(Application.id == new_app_id)
        result = await db_session.execute(stmt)
        created_app = result.scalar_one_or_none()

        # Pyright can sometimes raise a false positive on this assertion with SQLAlchemy models.
        # The code is correct; we are checking that the object was retrieved.
        assert created_app is not None  # type: ignore

        assert created_app.id == new_app_id
        assert created_app.status == 'draft'
        assert created_app.data == {}
