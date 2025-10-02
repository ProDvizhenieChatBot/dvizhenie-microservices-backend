"""
Integration tests for the file storage service API endpoints.
Uses the mocked s3_client from conftest.py.
"""
import io

import pytest
from httpx import AsyncClient

from app.core.config import settings


# --------------------------
# File Upload Tests
# --------------------------
class TestFileUploadEndpoint:

    @pytest.mark.asyncio
    async def test_upload_file_success(self, test_client: AsyncClient):
        file_content = b'This is a test file.'
        file_to_upload = {'file': ('test.txt', io.BytesIO(file_content), 'text/plain')}

        response = await test_client.post('/api/v1/files/', files=file_to_upload)
        assert response.status_code == 201

        data = response.json()
        assert 'file_id' in data
        assert data['filename'] == 'test.txt'
        assert data['content_type'] == 'text/plain'
        assert data['file_id'].endswith('.txt')

    @pytest.mark.asyncio
    async def test_upload_file_no_file(self, test_client: AsyncClient):
        response = await test_client.post('/api/v1/files/')
        assert response.status_code == 422


# --------------------------
# Download Link Tests
# --------------------------
class TestDownloadLinkEndpoint:

    @pytest.mark.asyncio
    async def test_get_download_link_success(self, test_client: AsyncClient):
        # Upload a file first
        file_content = b'Test PDF content'
        file_to_upload = {'file': ('test.pdf', io.BytesIO(file_content), 'application/pdf')}
        upload_resp = await test_client.post('/api/v1/files/', files=file_to_upload)
        file_id = upload_resp.json()['file_id']

        # Generate download link
        response = await test_client.get(f'/api/v1/files/{file_id}/download-link')
        assert response.status_code == 200
        data = response.json()
        url = data['download_url']
        assert url.startswith(settings.S3_PUBLIC_URL)
        assert file_id in url
        assert 'X-Amz-Test' in url

    @pytest.mark.asyncio
    async def test_get_download_link_not_found(self, test_client: AsyncClient):
        response = await test_client.get('/api/v1/files/non-existent-file.txt/download-link')
        assert response.status_code == 404
        assert response.json()['detail'] == 'File with id "non-existent-file.txt" not found.'
