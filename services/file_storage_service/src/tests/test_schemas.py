import pytest
from pydantic import ValidationError

from app.schemas.files import FileDownloadResponse, FileUploadResponse


@pytest.mark.unit
class TestFileUploadResponseSchema:
    """Tests for the FileUploadResponse Pydantic model."""

    def test_valid_schema_with_all_fields(self):
        """Test a valid payload with all fields."""
        data = {
            'file_id': '12345678-1234-5678-1234-567812345678.pdf',
            'filename': 'document.pdf',
            'content_type': 'application/pdf',
        }
        response = FileUploadResponse(**data)
        assert response.file_id == data['file_id']
        assert response.filename == data['filename']
        assert response.content_type == data['content_type']

    def test_valid_schema_with_only_required_fields(self):
        """Test a valid payload with only the required file_id field."""
        data = {'file_id': '12345678-1234-5678-1234-567812345678'}
        response = FileUploadResponse(**data)
        assert response.file_id == data['file_id']
        assert response.filename is None
        assert response.content_type is None

    def test_invalid_schema_missing_file_id(self):
        """Test that a validation error is raised if file_id is missing."""
        data = {'filename': 'document.pdf', 'content_type': 'application/pdf'}
        with pytest.raises(ValidationError):
            FileUploadResponse(**data)


@pytest.mark.unit
class TestFileDownloadResponseSchema:
    """Tests for the FileDownloadResponse Pydantic model."""

    def test_valid_schema_with_url(self):
        """Test a valid payload with a correct URL."""
        data = {'download_url': 'https://example.com/file.pdf?signature=abc123'}
        response = FileDownloadResponse(**data)
        assert str(response.download_url) == data['download_url']

    def test_invalid_schema_with_bad_url(self):
        """Test that a validation error is raised for an invalid URL."""
        data = {'download_url': 'this-is-not-a-valid-url'}
        with pytest.raises(ValidationError):
            FileDownloadResponse(**data)

    def test_invalid_schema_missing_url(self):
        """Test that a validation error is raised if download_url is missing."""
        with pytest.raises(ValidationError):
            FileDownloadResponse(**{})
