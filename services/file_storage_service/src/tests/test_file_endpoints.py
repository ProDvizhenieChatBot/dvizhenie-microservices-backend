"""
Integration tests for the File Storage Service API endpoints.
Includes edge cases and error scenarios to improve coverage.
"""

import io

import pytest
from botocore.exceptions import ClientError
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

    @pytest.mark.asyncio
    async def test_upload_file_no_extension(self, test_client: AsyncClient):
        """
        Test uploading a file with no extension.
        This exercises the Path(file.filename).suffix == '' branch.
        """
        file_content = b'No extension'
        file_to_upload = {'file': ('file', io.BytesIO(file_content), 'text/plain')}  # no extension
        response = await test_client.post('/api/v1/files/', files=file_to_upload)
        assert response.status_code == 201
        data = response.json()
        assert data['filename'] == 'file'
        assert data['file_id'].endswith('')  # No extension in file_id

    @pytest.mark.asyncio
    async def test_upload_file_s3_error(self, test_client: AsyncClient, s3_client):
        # Simulate an S3 upload failure
        async def fail_upload(*args, **kwargs):
            raise Exception('S3 failure')

        s3_client.upload_fileobj.side_effect = fail_upload

        file_content = b'Fail upload'
        file_to_upload = {'file': ('fail.txt', io.BytesIO(file_content), 'text/plain')}
        response = await test_client.post('/api/v1/files/', files=file_to_upload)
        assert response.status_code == 500
        assert 'Failed to upload file to S3' in response.json()['detail']


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

    @pytest.mark.asyncio
    async def test_get_download_link_head_object_error(self, test_client: AsyncClient, s3_client):
        # Simulate unknown S3 error
        async def head_object_fail(**kwargs):
            raise ClientError({'Error': {'Code': '500', 'Message': 'Internal Error'}}, 'HeadObject')

        s3_client.head_object.side_effect = head_object_fail

        file_id = 'testfile.txt'
        response = await test_client.get(f'/api/v1/files/{file_id}/download-link')
        assert response.status_code == 500
        assert 'An S3 error occurred' in response.json()['detail']
