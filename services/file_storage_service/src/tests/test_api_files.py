import io
import uuid
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError


@pytest.mark.unit
class TestFileUpload:
    """Unit test cases for the file upload endpoint."""

    def test_upload_file_success(self, client, override_s3_client):
        """Test successful file upload."""
        file_content = b'test file content'
        files = {'file': ('test.txt', io.BytesIO(file_content), 'text/plain')}

        # Mock successful upload
        override_s3_client.upload_fileobj.return_value = None

        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
            response = client.post('/api/v1/files/', files=files)

        assert response.status_code == 201
        data = response.json()
        assert data['file_id'] == '12345678-1234-5678-1234-567812345678.txt'
        assert data['filename'] == 'test.txt'
        assert data['content_type'] == 'text/plain'

        # Verify S3 upload was called
        override_s3_client.upload_fileobj.assert_called_once()

    def test_upload_file_without_extension(self, client, override_s3_client):
        """Test file upload without a file extension."""
        file_content = b'test file content'
        files = {'file': ('testfile', io.BytesIO(file_content), 'application/octet-stream')}

        override_s3_client.upload_fileobj.return_value = None

        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('87654321-4321-8765-4321-876543218765')
            response = client.post('/api/v1/files/', files=files)

        assert response.status_code == 201
        data = response.json()
        assert data['file_id'] == '87654321-4321-8765-4321-876543218765'

    def test_upload_file_s3_error(self, client, override_s3_client):
        """Test that a 500 error is returned if the S3 upload fails."""
        files = {'file': ('test.txt', io.BytesIO(b'content'), 'text/plain')}

        # Mock an S3 error
        override_s3_client.upload_fileobj.side_effect = Exception('S3 connection failed')

        response = client.post('/api/v1/files/', files=files)

        assert response.status_code == 500
        assert 'Failed to upload file to S3' in response.json()['detail']


@pytest.mark.unit
class TestFileDownload:
    """Unit test cases for the file download link endpoint."""

    def test_get_download_link_success(self, client, override_s3_client):
        """Test successful download link generation."""
        file_id = 'test-file-id.txt'

        # Mock that the file exists
        override_s3_client.head_object.return_value = None

        # Mock the presigned URL generation to return the internal URL
        internal_url = 'http://internal-s3:9000/test-bucket/test-file-id.txt?sig=123'
        override_s3_client.generate_presigned_url.return_value = internal_url

        response = client.get(f'/api/v1/files/{file_id}/download-link')

        assert response.status_code == 200
        data = response.json()
        # Assert that the response contains the correctly translated PUBLIC URL
        assert (
            data['download_url']
            == 'http://public-s3.example.com/test-bucket/test-file-id.txt?sig=123'
        )

        # Verify S3 calls
        override_s3_client.head_object.assert_called_once_with(Bucket='test-bucket', Key=file_id)
        override_s3_client.generate_presigned_url.assert_called_once_with(
            ClientMethod='get_object',
            Params={'Bucket': 'test-bucket', 'Key': file_id},
            ExpiresIn=3600,
        )

    def test_get_download_link_file_not_found(self, client, override_s3_client):
        """Test that a 404 error is returned for a non-existent file."""
        file_id = 'non-existent-file.txt'

        # Mock a '404 Not Found' error from S3
        error_response = {'Error': {'Code': '404', 'Message': 'Not Found'}}
        override_s3_client.head_object.side_effect = ClientError(error_response, 'HeadObject')

        response = client.get(f'/api/v1/files/{file_id}/download-link')

        assert response.status_code == 404
        assert f'File with id "{file_id}" not found' in response.json()['detail']

    def test_get_download_link_other_s3_error(self, client, override_s3_client):
        """Test that a 500 error is returned for other S3-related issues."""
        file_id = 'test-file-id.txt'

        # Mock a non-404 S3 error
        error_response = {'Error': {'Code': '500', 'Message': 'Internal Server Error'}}
        override_s3_client.head_object.side_effect = ClientError(error_response, 'HeadObject')

        response = client.get(f'/api/v1/files/{file_id}/download-link')

        assert response.status_code == 500
        assert 'An S3 error occurred' in response.json()['detail']
