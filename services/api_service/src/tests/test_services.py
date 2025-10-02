"""
Unit tests for service layer.

Tests the export_service and zip_service with mocked dependencies.
"""

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.db_models import Application, ApplicationFile
from app.services.export_service import generate_xlsx_export
from app.services.zip_service import create_documents_zip_archive


class TestExportService:
    """Test suite for XLSX export service."""

    def test_generate_xlsx_export_empty_list(self):
        """Test exporting an empty list of applications."""
        result = generate_xlsx_export([])

        assert isinstance(result, io.BytesIO)
        assert result.getvalue() == b''

    def test_generate_xlsx_export_with_applications(
        self, draft_application: Application, submitted_application: Application
    ):
        """Test generating XLSX from applications."""
        applications = [draft_application, submitted_application]
        result = generate_xlsx_export(applications)

        assert isinstance(result, io.BytesIO)
        assert len(result.getvalue()) > 0

        # Verify it contains Excel data (starts with PK for ZIP format)
        content = result.getvalue()
        assert content[:2] == b'PK'

    def test_generate_xlsx_flattens_data(self, draft_application: Application):
        """Test that nested JSON data is flattened in the export."""
        draft_application.data = {'name': 'John', 'address': {'city': 'NYC'}}

        result = generate_xlsx_export([draft_application])

        assert isinstance(result, io.BytesIO)
        assert len(result.getvalue()) > 0


class TestZipService:
    """Test suite for ZIP archive service."""

    @pytest.fixture
    def mock_settings(self):
        """Provides mock settings for testing."""
        settings = MagicMock()
        settings.FILE_STORAGE_SERVICE_URL = 'http://file-service:8000'
        settings.S3_PUBLIC_URL = 'http://localhost:9000'
        settings.S3_ENDPOINT_URL = 'http://minio:9000'
        return settings

    @pytest.fixture
    def application_with_mock_files(self):
        """Creates an application with mock file records."""
        app = MagicMock(spec=Application)
        app.id = 'test-uuid-123'

        file1 = MagicMock(spec=ApplicationFile)
        file1.file_id = 'file1.pdf'
        file1.original_filename = 'passport.pdf'
        file1.form_field_id = 'passport_scan'

        file2 = MagicMock(spec=ApplicationFile)
        file2.file_id = 'file2.jpg'
        file2.original_filename = 'photo.jpg'
        file2.form_field_id = 'beneficiary_photo'

        app.files = [file1, file2]
        return app

    @pytest.mark.asyncio
    @patch('app.services.zip_service.httpx.AsyncClient')
    async def test_create_zip_archive_success(
        self, mock_client_class, application_with_mock_files, mock_settings
    ):
        """Test successfully creating a ZIP archive from application files."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock the download link response
        link_response = AsyncMock()
        link_response.raise_for_status = MagicMock()
        link_response.json.return_value = {
            'download_url': 'http://localhost:9000/bucket/file1.pdf?signature=xyz'
        }

        # Mock the file content response
        content_response = AsyncMock()
        content_response.raise_for_status = MagicMock()
        content_response.content = b'fake pdf content'

        # Set up mock client to return different responses
        mock_client.get.side_effect = [
            link_response,  # First call for link
            content_response,  # Second call for content
            link_response,  # Third call for link (second file)
            content_response,  # Fourth call for content (second file)
        ]

        result = await create_documents_zip_archive(application_with_mock_files, mock_settings)

        assert isinstance(result, io.BytesIO)
        assert len(result.getvalue()) > 0

        # Verify it's a valid ZIP file (starts with PK)
        content = result.getvalue()
        assert content[:2] == b'PK'

    @pytest.mark.asyncio
    @patch('app.services.zip_service.httpx.AsyncClient')
    async def test_create_zip_archive_file_download_error(
        self, mock_client_class, application_with_mock_files, mock_settings
    ):
        """Test handling file download errors gracefully."""
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock a failed download
        from httpx import HTTPStatusError, Request, Response

        failed_response = Response(
            status_code=404,
            content=b'Not found',
            request=Request('GET', 'http://test.com'),
        )

        mock_client.get.side_effect = HTTPStatusError(
            'Not found', request=failed_response.request, response=failed_response
        )

        result = await create_documents_zip_archive(application_with_mock_files, mock_settings)

        # Should still return a ZIP, but with error files
        assert isinstance(result, io.BytesIO)
        assert len(result.getvalue()) > 0

    @pytest.mark.asyncio
    async def test_create_zip_archive_no_files(self, mock_settings):
        """Test creating ZIP for application with no files."""
        app = MagicMock(spec=Application)
        app.files = []

        result = await create_documents_zip_archive(app, mock_settings)

        # Should return an empty but valid ZIP
        assert isinstance(result, io.BytesIO)

        # Check if it's a valid empty ZIP
        content = result.getvalue()
        assert len(content) > 0
        assert content[:2] == b'PK'
