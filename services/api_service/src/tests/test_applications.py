# # services/api_service/src/tests/test_applications.py
# import os
# from unittest.mock import MagicMock, patch

# import pytest


# # Set test environment variables before importing app modules
# os.environ.setdefault('POSTGRES_HOST', 'test')
# os.environ.setdefault('POSTGRES_DB', 'test')
# os.environ.setdefault('POSTGRES_USER', 'test')
# os.environ.setdefault('POSTGRES_PASSWORD', 'test')

# # Mock the database engine creation to prevent actual connections
# with patch('app.core.db.create_async_engine'), patch('app.core.db.async_sessionmaker'):
#     from app.api.applications import (
#         create_draft_application,
#         get_application_data,
#         save_application_progress,
#     )
#     from app.schemas.applications import ApplicationCreate, ApplicationUpdate


# class MockApplication:
#     """Mock Application model for testing."""

#     def __init__(self, id=1, status='draft', data=None):
#         self.id = id
#         self.status = status
#         self.data = data or {}


# class MockSession:
#     """Custom mock session to avoid AsyncMock issues."""

#     def __init__(self):
#         self.add_calls = []
#         self.commit_calls = []
#         self.refresh_calls = []

#     def add(self, obj):
#         """Non-async add method."""
#         self.add_calls.append(obj)

#     async def commit(self):
#         """Async commit method."""
#         self.commit_calls.append(True)

#     async def refresh(self, obj):
#         """Async refresh method."""
#         self.refresh_calls.append(obj)

#     async def execute(self, query):
#         """Async execute method for query operations."""
#         # This will be overridden in individual tests
#         pass


# class TestApplicationEndpointFunctions:
#     """Test the endpoint functions directly without HTTP layer."""

#     @patch('app.api.applications.Application')
#     async def test_create_draft_application_success(self, mock_application_class):
#         """Test successful creation of a draft application."""
#         # Use custom mock session to avoid AsyncMock issues
#         mock_session = MockSession()

#         # Mock the Application model instance
#         mock_app = MockApplication(id=1, status='draft', data={})
#         mock_application_class.return_value = mock_app

#         # Call the endpoint function directly
#         application_in = ApplicationCreate()
#         result = await create_draft_application(application_in, mock_session)

#         # Verify the result
#         assert result == mock_app
#         assert result.status == 'draft'
#         assert result.data == {}

#         # Verify database operations were called
#         assert len(mock_session.add_calls) == 1
#         assert mock_session.add_calls[0] == mock_app
#         assert len(mock_session.commit_calls) == 1
#         assert len(mock_session.refresh_calls) == 1

#     @patch('app.api.applications.select')
#     async def test_get_application_data_success(self, mock_select):
#         """Test successful retrieval of application data."""
#         # Mock database session - use MagicMock instead of AsyncMock
#         mock_session = MagicMock()

#         # Mock the application
#         mock_app = MockApplication(id=1, status='draft', data={'test': 'data'})

#         # Mock query result
#         mock_result = MagicMock()
#         mock_result.scalar_one_or_none.return_value = mock_app

#         # Create an async function that returns the mock_result
#         async def mock_execute(*args, **kwargs):
#             return mock_result

#         mock_session.execute = mock_execute

#         # Call the endpoint function
#         result = await get_application_data(1, mock_session)

#         # Verify the result
#         assert result == mock_app
#         assert result.id == 1
#         assert result.status == 'draft'
#         assert result.data == {'test': 'data'}

#     @patch('app.api.applications.select')
#     async def test_get_application_data_not_found(self, mock_select):
#         """Test retrieval of non-existent application."""
#         # Mock database session - use MagicMock instead of AsyncMock
#         mock_session = MagicMock()

#         # Mock empty query result
#         mock_result = MagicMock()
#         mock_result.scalar_one_or_none.return_value = None

#         # Create an async function that returns the mock_result
#         async def mock_execute(*args, **kwargs):
#             return mock_result

#         mock_session.execute = mock_execute

#         # Call the endpoint function and expect HTTPException
#         from fastapi import HTTPException

#         with pytest.raises(HTTPException) as exc_info:
#             await get_application_data(99999, mock_session)

#         assert exc_info.value.status_code == 404
#         assert 'not found' in str(exc_info.value.detail).lower()

#     @patch('app.api.applications.select')
#     async def test_save_application_progress_success(self, mock_select):
#         """Test successful saving of application progress."""
#         # Mock database session - use MagicMock for non-async methods
#         mock_session = MagicMock()

#         # Mock the application
#         mock_app = MockApplication(id=1, status='draft', data={})

#         # Mock query result
#         mock_result = MagicMock()
#         mock_result.scalar_one_or_none.return_value = mock_app

#         # Create async functions for session operations
#         async def mock_execute(*args, **kwargs):
#             return mock_result

#         async def mock_commit():
#             pass

#         async def mock_refresh(app):
#             pass

#         mock_session.execute = mock_execute
#         mock_session.commit = mock_commit
#         mock_session.refresh = mock_refresh
#         mock_session.add = MagicMock()  # add is not async

#         # Prepare update data
#         test_data = {'name': 'Test', 'value': 123}
#         application_update = ApplicationUpdate(data=test_data)

#         # Call the endpoint function
#         result = await save_application_progress(1, application_update, mock_session)

#         # Verify the result
#         assert result == mock_app
#         assert result.data == test_data

#         # Verify database operations were called
#         mock_session.add.assert_called_once_with(mock_app)

#     @patch('app.api.applications.select')
#     async def test_save_application_progress_not_found(self, mock_select):
#         """Test saving progress for non-existent application."""
#         # Mock database session - use MagicMock instead of AsyncMock
#         mock_session = MagicMock()

#         # Mock empty query result
#         mock_result = MagicMock()
#         mock_result.scalar_one_or_none.return_value = None

#         # Create an async function that returns the mock_result
#         async def mock_execute(*args, **kwargs):
#             return mock_result

#         mock_session.execute = mock_execute

#         # Prepare update data
#         test_data = {'name': 'Test'}
#         application_update = ApplicationUpdate(data=test_data)

#         # Call the endpoint function and expect HTTPException
#         from fastapi import HTTPException

#         with pytest.raises(HTTPException) as exc_info:
#             await save_application_progress(99999, application_update, mock_session)

#         assert exc_info.value.status_code == 404
#         assert 'not found' in str(exc_info.value.detail).lower()

#     @patch('app.api.applications.select')
#     async def test_save_application_progress_complex_data(self, mock_select):
#         """Test saving complex nested JSON data."""
#         # Mock database session
#         mock_session = MagicMock()

#         # Mock the application
#         mock_app = MockApplication(id=1, status='draft', data={})

#         # Mock query result
#         mock_result = MagicMock()
#         mock_result.scalar_one_or_none.return_value = mock_app

#         # Create async functions for session operations
#         async def mock_execute(*args, **kwargs):
#             return mock_result

#         async def mock_commit():
#             pass

#         async def mock_refresh(app):
#             pass

#         mock_session.execute = mock_execute
#         mock_session.commit = mock_commit
#         mock_session.refresh = mock_refresh
#         mock_session.add = MagicMock()

#         # Complex test data
#         complex_data = {
#             'personal': {
#                 'name': 'Тест',
#                 'contacts': {'phone': '+79123456789', 'emails': ['test@example.com']},
#             },
#             'documents': [{'type': 'passport', 'number': '1234567890'}],
#             'flags': {'consent': True, 'newsletter': False},
#         }

#         application_update = ApplicationUpdate(data=complex_data)

#         # Call the endpoint function
#         result = await save_application_progress(1, application_update, mock_session)

#         # Verify the result
#         assert result == mock_app
#         assert result.data == complex_data

#
#     @patch('app.api.applications.select')
#     async def test_save_application_progress_null_values(self, mock_select):
#         """Test saving data with null values."""
#         # Mock database session
#         mock_session = MagicMock()

#         # Mock the application
#         mock_app = MockApplication(id=1, status='draft', data={})

#         # Mock query result
#         mock_result = MagicMock()
#         mock_result.scalar_one_or_none.return_value = mock_app

#         # Create async functions for session operations
#         async def mock_execute(*args, **kwargs):
#             return mock_result

#         async def mock_commit():
#             pass

#         async def mock_refresh(app):
#             pass

#         mock_session.execute = mock_execute
#         mock_session.commit = mock_commit
#         mock_session.refresh = mock_refresh
#         mock_session.add = MagicMock()

#         # Data with null values
#         data_with_nulls = {
#             'required_field': 'value',
#             'optional_field': None,
#             'nested': {'also_null': None, 'has_value': 'test'},
#         }

#         application_update = ApplicationUpdate(data=data_with_nulls)

#         # Call the endpoint function
#         result = await save_application_progress(1, application_update, mock_session)

#         # Verify the result
#         assert result == mock_app
#         assert result.data == data_with_nulls

#     @patch('app.api.applications.Application')
#     async def test_create_draft_sets_correct_defaults(self, mock_application_class):
#         """Test that draft creation sets correct default values."""
#         # Mock database session
#         mock_session = MockSession()

#         # Mock the Application model instance
#         mock_app = MockApplication(id=5, status='draft', data={})
#         mock_application_class.return_value = mock_app

#         # Call the endpoint function
#         application_in = ApplicationCreate()
#         result = await create_draft_application(application_in, mock_session)

#         # Verify that Application was called with correct parameters
#         mock_application_class.assert_called_once_with(status='draft', data={})

#         # Verify the result
#         assert result.status == 'draft'
#         assert result.data == {}

#     async def test_application_update_schema_validation(self):
#         """Test that ApplicationUpdate schema validates data correctly."""
#         # Valid data should work
#         valid_data = {'field1': 'value1', 'field2': {'nested': 'data'}}
#         update = ApplicationUpdate(data=valid_data)
#         assert update.data == valid_data

#         # Empty data should work
#         empty_update = ApplicationUpdate(data={})
#         assert empty_update.data == {}

#         # None values should work
#         null_data = {'field': None}
#         null_update = ApplicationUpdate(data=null_data)
#         assert null_update.data == null_data

#     async def test_application_create_schema_validation(self):
#         """Test that ApplicationCreate schema works correctly."""
#         # ApplicationCreate should accept no parameters
#         create = ApplicationCreate()
#         assert create is not None

#         # Should work with empty dict too
#         create_with_dict = ApplicationCreate(**{})
#         assert create_with_dict is not None


# class TestWorkflowIntegration:
#     """Test workflow scenarios with multiple function calls."""

#     @patch('app.api.applications.select')
#     @patch('app.api.applications.Application')
#     async def test_complete_application_workflow(self, mock_application_class, mock_select):
#         """Test complete workflow: create -> update -> retrieve."""
#         # Mock database session
#         mock_session = MagicMock()

#         # Step 1: Create application
#         mock_app = MockApplication(id=1, status='draft', data={})
#         mock_application_class.return_value = mock_app

#         # Mock async operations for create
#         async def mock_commit():
#             pass

#         async def mock_refresh(app):
#             pass

#         mock_session.commit = mock_commit
#         mock_session.refresh = mock_refresh
#         mock_session.add = MagicMock()

#         # Create the application
#         application_in = ApplicationCreate()
#         created_app = await create_draft_application(application_in, mock_session)

#         assert created_app.status == 'draft'
#         assert created_app.data == {}

#         # Step 2: Update application with data
#         test_data = {'name': 'Test User', 'email': 'test@example.com'}

#         # Mock query for update
#         mock_result = MagicMock()
#         mock_result.scalar_one_or_none.return_value = mock_app

#         async def mock_execute(*args, **kwargs):
#             return mock_result

#         mock_session.execute = mock_execute

#         # Update the application
#         application_update = ApplicationUpdate(data=test_data)
#         updated_app = await save_application_progress(1, application_update, mock_session)

#         # Verify the data was set correctly
#         assert updated_app.data == test_data

#         # Step 3: Retrieve the application
#         retrieved_app = await get_application_data(1, mock_session)

#         # Verify we get the same application
#         assert retrieved_app == mock_app
#         assert retrieved_app.id == 1
#         assert retrieved_app.status == 'draft'
