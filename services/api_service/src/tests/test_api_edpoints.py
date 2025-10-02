"""
Integration tests for API endpoints.

Tests all public and admin endpoints using a test client and mocked dependencies.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient

from app.models.db_models import Application


class TestSessionEndpoints:
    """Test suite for session management endpoints."""

    async def test_create_telegram_session_new_user(self, test_client: AsyncClient):
        """Test creating a new session for a Telegram user."""
        payload = {'telegram_id': 123456789}
        response = await test_client.post('/api/v1/sessions/telegram', json=payload)

        assert response.status_code == 200
        data = response.json()
        assert 'application_uuid' in data
        assert uuid.UUID(data['application_uuid'])

    async def test_create_telegram_session_resume_draft(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test resuming an existing draft session."""
        payload = {'telegram_id': draft_application.telegram_id}
        response = await test_client.post('/api/v1/sessions/telegram', json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data['application_uuid'] == str(draft_application.id)

    async def test_create_web_session(self, test_client: AsyncClient):
        """Test creating a new web session."""
        response = await test_client.post('/api/v1/sessions/web')

        assert response.status_code == 200
        data = response.json()
        assert 'application_uuid' in data
        assert uuid.UUID(data['application_uuid'])

    async def test_get_telegram_status_found(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test getting status for an existing Telegram user."""
        response = await test_client.get(
            '/api/v1/sessions/telegram/status',
            params={'telegram_id': draft_application.telegram_id},
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'draft'

    async def test_get_telegram_status_not_found(self, test_client: AsyncClient):
        """Test getting status when no application exists."""
        response = await test_client.get(
            '/api/v1/sessions/telegram/status', params={'telegram_id': 999999999}
        )

        assert response.status_code == 404


class TestApplicationPublicEndpoints:
    """Test suite for public application endpoints (used by Mini App)."""

    async def test_get_application_status(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test retrieving application status."""
        response = await test_client.get(
            f'/api/v1/applications/{draft_application.id}/public/status'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'draft'

    async def test_get_application_status_not_found(self, test_client: AsyncClient):
        """Test getting status for non-existent application."""
        fake_uuid = uuid.uuid4()
        response = await test_client.get(f'/api/v1/applications/{fake_uuid}/public/status')

        assert response.status_code == 404

    async def test_get_application_data(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test retrieving application data for editing."""
        response = await test_client.get(f'/api/v1/applications/{draft_application.id}/public')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == str(draft_application.id)
        assert data['status'] == 'draft'
        assert 'data' in data

    async def test_save_application_progress(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test saving progress from Mini App."""
        update_payload = {'data': {'step1': 'completed', 'name': 'John Doe'}}

        response = await test_client.patch(
            f'/api/v1/applications/{draft_application.id}/public', json=update_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data['data']['name'] == 'John Doe'

    async def test_save_application_progress_non_draft(
        self, test_client: AsyncClient, submitted_application: Application
    ):
        """Test that only draft applications can be updated."""
        update_payload = {'data': {'new_field': 'value'}}

        response = await test_client.patch(
            f'/api/v1/applications/{submitted_application.id}/public',
            json=update_payload,
        )

        assert response.status_code == 400

    async def test_link_file_to_application(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test linking a file to an application."""
        file_link_payload = {
            'file_id': 'test-file-123.pdf',
            'original_filename': 'passport.pdf',
            'form_field_id': 'passport_scan',
        }

        response = await test_client.post(
            f'/api/v1/applications/{draft_application.id}/files',
            json=file_link_payload,
        )

        assert response.status_code == 201
        data = response.json()
        assert data['message'] == 'File linked successfully'

    async def test_submit_application(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test submitting a draft application."""
        response = await test_client.post(f'/api/v1/applications/{draft_application.id}/submit')

        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Application submitted successfully'

    async def test_submit_application_already_submitted(
        self, test_client: AsyncClient, submitted_application: Application
    ):
        """Test that already submitted applications cannot be resubmitted."""
        response = await test_client.post(f'/api/v1/applications/{submitted_application.id}/submit')

        assert response.status_code == 400


class TestApplicationAdminEndpoints:
    """Test suite for admin endpoints."""

    async def test_get_all_applications(
        self,
        test_client: AsyncClient,
        draft_application: Application,
        submitted_application: Application,
    ):
        """Test retrieving all applications as admin."""
        response = await test_client.get('/api/v1/admin/applications/')

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert any(app['id'] == str(draft_application.id) for app in data)

    async def test_get_all_applications_with_filter(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test filtering applications by status."""
        response = await test_client.get('/api/v1/admin/applications/', params={'status': 'draft'})

        assert response.status_code == 200
        data = response.json()
        assert all(app['status'] == 'draft' for app in data)

    async def test_get_application_details_admin(
        self, test_client: AsyncClient, application_with_files: Application
    ):
        """Test getting detailed application info with files."""
        response = await test_client.get(f'/api/v1/admin/applications/{application_with_files.id}')

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == str(application_with_files.id)
        assert 'files' in data
        assert len(data['files']) == 2

    async def test_update_application_status(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test updating application status as admin."""
        update_payload = {'status': 'in_progress'}

        response = await test_client.patch(
            f'/api/v1/admin/applications/{draft_application.id}', json=update_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'in_progress'

    async def test_add_admin_comment(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test adding an admin comment to an application."""
        update_payload = {'admin_comment': 'Waiting for additional documents'}

        response = await test_client.patch(
            f'/api/v1/admin/applications/{draft_application.id}', json=update_payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data['admin_comment'] == 'Waiting for additional documents'

    @patch('app.services.export_service.generate_xlsx_export')
    async def test_export_applications(self, mock_export: MagicMock, test_client: AsyncClient):
        """Test exporting applications to XLSX."""
        mock_export.return_value = MagicMock()
        mock_export.return_value.seek = MagicMock()
        mock_export.return_value.read = MagicMock(return_value=b'fake xlsx data')

        response = await test_client.get('/api/v1/admin/applications/export')

        assert response.status_code == 200
        assert (
            response.headers['content-type']
            == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    @patch('app.services.zip_service.create_documents_zip_archive')
    async def test_download_documents_as_zip(
        self,
        mock_zip: AsyncMock,
        test_client: AsyncClient,
        application_with_files: Application,
    ):
        """Test downloading application documents as ZIP."""
        mock_zip.return_value = MagicMock()
        mock_zip.return_value.seek = MagicMock()
        mock_zip.return_value.read = MagicMock(return_value=b'fake zip data')

        response = await test_client.get(
            f'/api/v1/admin/applications/{application_with_files.id}/download-documents'
        )

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/zip'

    async def test_download_documents_no_files(
        self, test_client: AsyncClient, draft_application: Application
    ):
        """Test downloading documents when none exist."""
        response = await test_client.get(
            f'/api/v1/admin/applications/{draft_application.id}/download-documents'
        )

        assert response.status_code == 404


class TestFormSchemaEndpoints:
    """Test suite for form schema endpoints."""

    async def test_get_active_schema(self, test_client: AsyncClient, active_form_schema):
        """Test retrieving the active form schema."""
        response = await test_client.get('/api/v1/forms/schema/active')

        assert response.status_code == 200
        data = response.json()
        assert data['version'] == '1.0'
        assert 'steps' in data

    async def test_get_active_schema_none_exists(self, test_client: AsyncClient):
        """Test error when no active schema exists."""
        response = await test_client.get('/api/v1/forms/schema/active')

        assert response.status_code == 500

    async def test_upload_new_schema(self, test_client: AsyncClient, sample_form_schema: dict):
        """Test uploading a new form schema as admin."""
        upload_payload = {'version': '2.0', 'schema_data': sample_form_schema}

        response = await test_client.post('/api/v1/admin/forms/schema', json=upload_payload)

        assert response.status_code == 201
        data = response.json()
        assert 'version 2.0 has been uploaded' in data['message']


class TestHealthCheck:
    """Test suite for health check endpoint."""

    async def test_health_check(self, test_client: AsyncClient):
        """Test the health check endpoint."""
        response = await test_client.get('/api/v1/health')

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        assert data['service'] == 'API Service'
