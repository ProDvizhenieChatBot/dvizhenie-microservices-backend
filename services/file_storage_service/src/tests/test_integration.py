import io

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_s3

from app.main import app


@pytest.mark.integration
@mock_s3
class TestIntegrationWithMoto:
    """
    Integration tests using moto to create a mock S3 environment.
    This tests the full application logic against a realistic S3 API.
    """

    @pytest.fixture(autouse=True)
    def setup_s3_and_client(self, monkeypatch):
        """
        Set up the moto S3 mock environment before each test in this class.
        """
        # We must override the S3 dependency to ensure the app uses a client
        # that is configured to talk to the moto mock server, not a real one.
        # Moto automatically mocks boto3, so we can create a real client.
        s3_client = boto3.client(
            's3',
            region_name='us-east-1',
            aws_access_key_id='testing',
            aws_secret_access_key='testing',
        )
        # The bucket name comes from the test settings in conftest.py
        bucket_name = 'test-bucket'
        s3_client.create_bucket(Bucket=bucket_name)

        # To make the FastAPI app use this moto-patched client, we need a
        # dependency override that yields a moto-configured aioboto3 client.
        # This is a bit complex, but necessary for async integration.
        import aioboto3

        async def get_moto_s3_client():
            session = aioboto3.Session(
                aws_access_key_id='testing',
                aws_secret_access_key='testing',
                region_name='us-east-1',
            )
            # Moto's mock endpoint is typically at http://localhost:5000
            # However, for moto's decorator, it transparently patches boto3.
            async with session.client('s3', endpoint_url=None) as async_client:
                yield async_client

        app.dependency_overrides[app.s3_client.get_s3_client] = get_moto_s3_client

        # Create the TestClient for making requests to the app
        self.client = TestClient(app)
        yield
        # Teardown: clear dependency overrides
        app.dependency_overrides.clear()

    def test_full_upload_and_download_cycle(self):
        """
        Test the complete cycle:
        1. Upload a file to the service.
        2. Verify the service returns a file_id.
        3. Request a download link for that file_id.
        4. Verify the link is valid and points to the correct public URL.
        """
        # 1. Upload a file
        file_content = b'integration test file content'
        files = {'file': ('integration.txt', io.BytesIO(file_content), 'text/plain')}

        upload_response = self.client.post('/api/v1/files/', files=files)
        assert upload_response.status_code == 201

        upload_data = upload_response.json()
        file_id = upload_data['file_id']
        assert file_id.endswith('.txt')

        # 2. Get the download link for the uploaded file
        download_link_response = self.client.get(f'/api/v1/files/{file_id}/download-link')
        assert download_link_response.status_code == 200

        download_data = download_link_response.json()
        assert 'download_url' in download_data

        # 3. Verify the URL points to the public domain from test settings
        public_url_base = 'http://public-s3.example.com/test-bucket'
        assert download_data['download_url'].startswith(public_url_base)
