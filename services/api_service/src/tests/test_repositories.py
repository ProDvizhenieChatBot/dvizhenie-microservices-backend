"""
Unit tests for repository layer.

Tests the ApplicationRepository and FormSchemaRepository classes
using an in-memory SQLite database.
"""

import uuid
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Application, FormSchema
from app.repositories.applications import ApplicationRepository
from app.repositories.forms import FormSchemaRepository
from app.schemas.applications import (
    ApplicationAdminUpdate,
    ApplicationStatus,
    ApplicationUpdate,
    FileLinkRequest,
)
from app.schemas.forms import FormSchemaUpload


class TestApplicationRepository:
    """Test suite for ApplicationRepository."""

    @pytest.fixture
    def repo(self, db_session: AsyncSession) -> ApplicationRepository:
        """Provides a repository instance for each test."""
        return ApplicationRepository(session=db_session)

    async def test_get_by_uuid_existing(
        self, repo: ApplicationRepository, draft_application: Application
    ):
        """Test retrieving an application by its UUID."""
        result = await repo.get_by_uuid(draft_application.id)

        assert result is not None
        assert isinstance(result, Application)
        assert result.id == draft_application.id
        assert result.status == 'draft'

    async def test_get_by_uuid_nonexistent(self, repo: ApplicationRepository):
        """Test retrieving a non-existent application returns None."""
        result = await repo.get_by_uuid(uuid.uuid4())
        assert result is None

    async def test_get_by_uuid_with_files(
        self, repo: ApplicationRepository, application_with_files: Application
    ):
        """Test retrieving an application with its related files."""
        result = await repo.get_by_uuid(application_with_files.id, with_files=True)
        assert result is not None
        app_with_files = cast(Application, result)

        assert isinstance(app_with_files, Application)
        assert len(app_with_files.files) == 2
        assert app_with_files.files[0].file_id in ['file1.pdf', 'file2.jpg']

    async def test_get_draft_by_telegram_id_existing(
        self, repo: ApplicationRepository, draft_application: Application
    ):
        """Test finding a draft application by telegram_id."""
        result = await repo.get_draft_by_telegram_id(draft_application.telegram_id)

        assert result is not None
        assert isinstance(result, Application)
        assert result.id == draft_application.id
        assert result.status == ApplicationStatus.DRAFT.value

    async def test_get_draft_by_telegram_id_nonexistent(self, repo: ApplicationRepository):
        """Test that searching for a non-existent telegram_id returns None."""
        result = await repo.get_draft_by_telegram_id(999999999)
        assert result is None

    async def test_get_draft_by_telegram_id_only_draft(
        self, repo: ApplicationRepository, submitted_application: Application
    ):
        """Test that only draft applications are returned, not submitted ones."""
        result = await repo.get_draft_by_telegram_id(submitted_application.telegram_id)
        assert result is None

    async def test_get_latest_by_telegram_id(
        self, repo: ApplicationRepository, draft_application: Application
    ):
        """Test retrieving the most recent application for a telegram user."""
        result = await repo.get_latest_by_telegram_id(draft_application.telegram_id)

        assert result is not None
        assert isinstance(result, Application)
        assert result.id == draft_application.id

    async def test_get_all_no_filter(
        self,
        repo: ApplicationRepository,
        draft_application: Application,
        submitted_application: Application,
    ):
        """Test retrieving all applications without filters."""
        results = await repo.get_all(limit=10, offset=0)

        assert len(results) == 2
        assert any(app.id == draft_application.id for app in results)
        assert any(app.id == submitted_application.id for app in results)

    async def test_get_all_with_status_filter(
        self,
        repo: ApplicationRepository,
        draft_application: Application,
        submitted_application: Application,
    ):
        """Test retrieving applications filtered by status."""
        results = await repo.get_all(status=ApplicationStatus.DRAFT, limit=10)

        assert len(results) == 1
        assert results[0].id == draft_application.id

    async def test_get_all_pagination(
        self,
        repo: ApplicationRepository,
        draft_application: Application,
        submitted_application: Application,
    ):
        """Test pagination parameters work correctly."""
        results = await repo.get_all(limit=1, offset=0)
        assert len(results) == 1

        results_page_2 = await repo.get_all(limit=1, offset=1)
        assert len(results_page_2) == 1
        assert results[0].id != results_page_2[0].id

    async def test_create_for_telegram_user(
        self, repo: ApplicationRepository, db_session: AsyncSession
    ):
        """Test creating a new application for a Telegram user."""
        telegram_id = 111222333
        result = await repo.create_for_telegram_user(telegram_id)

        assert result.id is not None
        assert result.telegram_id == telegram_id
        assert result.status == ApplicationStatus.DRAFT.value
        assert result.data == {}

    async def test_create_for_web_user(self, repo: ApplicationRepository, db_session: AsyncSession):
        """Test creating a new application for a web user."""
        result = await repo.create_for_web_user()

        assert result.id is not None
        assert result.telegram_id is None
        assert result.status == ApplicationStatus.DRAFT.value
        assert result.data == {}

    async def test_update_progress(
        self, repo: ApplicationRepository, draft_application: Application
    ):
        """Test updating application data."""
        update_data = ApplicationUpdate(data={'new_field': 'new_value'})
        result = await repo.update_progress(draft_application, update_data)

        assert result.data == {'new_field': 'new_value'}

    async def test_update_admin_details_status(
        self, repo: ApplicationRepository, draft_application: Application
    ):
        """Test updating application status by admin."""
        update_data = ApplicationAdminUpdate(status=ApplicationStatus.IN_PROGRESS)
        result = await repo.update_admin_details(draft_application, update_data)

        assert result.status == ApplicationStatus.IN_PROGRESS.value

    async def test_update_admin_details_comment(
        self, repo: ApplicationRepository, draft_application: Application
    ):
        """Test adding admin comment to application."""
        update_data = ApplicationAdminUpdate(admin_comment='Needs more documents')
        result = await repo.update_admin_details(draft_application, update_data)

        assert result.admin_comment == 'Needs more documents'

    async def test_submit_application(
        self, repo: ApplicationRepository, draft_application: Application
    ):
        """Test submitting a draft application."""
        result = await repo.submit_application(draft_application)

        assert result.status == ApplicationStatus.NEW.value

    async def test_link_file(self, repo: ApplicationRepository, draft_application: Application):
        """Test linking a file to an application."""
        file_link = FileLinkRequest(
            file_id='test-file.pdf',
            original_filename='document.pdf',
            form_field_id='passport_scan',
        )

        await repo.link_file(draft_application.id, file_link)

        # Verify the file was linked
        result = await repo.get_by_uuid(draft_application.id, with_files=True)
        assert result is not None
        app_with_files = cast(Application, result)

        assert isinstance(app_with_files, Application)
        assert len(app_with_files.files) == 1
        assert app_with_files.files[0].file_id == 'test-file.pdf'


class TestFormSchemaRepository:
    """Test suite for FormSchemaRepository."""

    @pytest.fixture
    def repo(self, db_session: AsyncSession) -> FormSchemaRepository:
        """Provides a repository instance for each test."""
        return FormSchemaRepository(session=db_session)

    async def test_get_active_schema_exists(self, repo: FormSchemaRepository, active_form_schema):
        """Test retrieving the active form schema."""
        result = await repo.get_active_schema()

        assert result is not None
        schema = cast(FormSchema, result)

        assert isinstance(schema, FormSchema)
        assert schema.is_active is True
        assert schema.version == '1.0'

    async def test_get_active_schema_none(self, repo: FormSchemaRepository):
        """Test retrieving active schema when none exists."""
        result = await repo.get_active_schema()
        assert result is None

    async def test_create_and_set_active_schema(
        self, repo: FormSchemaRepository, sample_form_schema: dict
    ):
        """Test creating a new schema and setting it as active."""
        schema_upload = FormSchemaUpload(version='2.0', schema_data=sample_form_schema)

        result = await repo.create_and_set_active_schema(schema_upload)

        assert result.version == '2.0'
        assert result.is_active is True
        assert result.schema_data == sample_form_schema

    async def test_create_and_set_active_deactivates_old(
        self, repo: FormSchemaRepository, active_form_schema, sample_form_schema: dict
    ):
        """Test that creating a new schema deactivates the old one."""
        new_schema_upload = FormSchemaUpload(version='2.0', schema_data=sample_form_schema)

        new_schema = await repo.create_and_set_active_schema(new_schema_upload)

        # Verify old schema is deactivated
        result = await repo.get_active_schema()
        assert result is not None
        old_schema = cast(FormSchema, result)

        assert isinstance(old_schema, FormSchema)
        assert old_schema.id == new_schema.id
        assert old_schema.version == '2.0'
