import os
from unittest.mock import patch

import pytest

from app.core.config import Settings


@pytest.mark.unit
class TestSettings:
    """Unit tests for the configuration settings."""

    def test_settings_loading_from_env_vars(self):
        """Test that settings are correctly loaded from environment variables."""
        env_vars = {
            'S3_ENDPOINT_URL': 'http://test-s3:9000',
            'S3_PUBLIC_URL': 'http://public.test.com',
            'MINIO_ROOT_USER': 'test_admin',
            'MINIO_ROOT_PASSWORD': 'test_password',
            'MINIO_BUCKET_NAME': 'my-test-bucket',
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert env_vars['S3_ENDPOINT_URL'] == settings.S3_ENDPOINT_URL
            assert env_vars['S3_PUBLIC_URL'] == settings.S3_PUBLIC_URL
            assert env_vars['MINIO_ROOT_USER'] == settings.MINIO_ROOT_USER
            assert env_vars['MINIO_ROOT_PASSWORD'] == settings.MINIO_ROOT_PASSWORD
            assert env_vars['MINIO_BUCKET_NAME'] == settings.MINIO_BUCKET_NAME

    def test_default_app_title_is_present(self):
        """Test that the default APP_TITLE is set if not provided in env."""
        # Minimal required env vars
        env_vars = {
            'S3_ENDPOINT_URL': 'http://test-s3:9000',
            'S3_PUBLIC_URL': 'http://public.test.com',
            'MINIO_ROOT_USER': 'test_admin',
            'MINIO_ROOT_PASSWORD': 'test_password',
            'MINIO_BUCKET_NAME': 'my-test-bucket',
        }
        with patch.dict(os.environ, env_vars):
            settings = Settings()
            assert settings.APP_TITLE == 'Charity MVP - File Storage Service'
