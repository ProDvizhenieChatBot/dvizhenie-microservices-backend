# API Service Testing Guide

This guide explains how to run and maintain the test suite for the `api-service`.

## Test Structure

```
services/api_service/
├── src/
│   └── app/         # Application code
└── tests/           # Test files
    ├── conftest.py              # Shared fixtures and configuration
    ├── test_repositories.py     # Repository layer tests
    ├── test_api_endpoints.py    # API endpoint integration tests
    └── test_services.py         # Service layer tests
```

## Setup

### 1. Install Development Dependencies

```bash
cd services/api_service
uv sync
```

This installs all dependencies including test libraries:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `aiosqlite` - In-memory database for tests
- `pytest-cov` - Code coverage reporting

### 2. Running Tests

**Run all tests:**
```bash
uv run pytest
```

**Run with coverage report:**
```bash
uv run pytest --cov=app --cov-report=html
```

**Run specific test file:**
```bash
uv run pytest tests/test_repositories.py
```

**Run specific test class:**
```bash
uv run pytest tests/test_repositories.py::TestApplicationRepository
```

**Run specific test:**
```bash
uv run pytest tests/test_repositories.py::TestApplicationRepository::test_get_by_uuid_existing
```

**Run tests with verbose output:**
```bash
uv run pytest -vv
```

**Run tests and stop at first failure:**
```bash
uv run pytest -x
```

## Test Categories

### Repository Tests (`test_repositories.py`)
Tests the data access layer in isolation:
- CRUD operations
- Query filtering and pagination
- Relationship loading
- Transaction handling

**Example:**
```python
async def test_get_by_uuid_existing(
    repo: ApplicationRepository, draft_application: Application
):
    """Test retrieving an application by its UUID."""
    result = await repo.get_by_uuid(draft_application.id)
    assert result is not None
    assert result.id == draft_application.id
```

### Service Tests (`test_services.py`)
Tests business logic services with mocked external dependencies:
- XLSX export generation
- ZIP archive creation
- File downloading and packaging

**Example:**
```python
@patch('app.services.zip_service.httpx.AsyncClient')
async def test_create_zip_archive_success(
    mock_client_class, application_with_mock_files, mock_settings
):
    """Test successfully creating a ZIP archive."""
    # Arrange
    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    
    # Act
    result = await create_documents_zip_archive(app, settings)
    
    # Assert
    assert isinstance(result, io.BytesIO)
```

### API Endpoint Tests (`test_api_endpoints.py`)
Integration tests for HTTP endpoints:
- Request/response validation
- Status codes
- Error handling
- Authentication (when implemented)

**Example:**
```python
async def test_create_telegram_session_new_user(test_client: AsyncClient):
    """Test creating a new session for a Telegram user."""
    payload = {'telegram_id': 123456789}
    response = await test_client.post('/api/v1/sessions/telegram', json=payload)
    
    assert response.status_code == 200
    assert 'application_uuid' in response.json()
```

## Fixtures

The `conftest.py` file provides reusable fixtures:

### Database Fixtures
- `db_session` - Clean in-memory database for each test
- `test_client` - HTTP client with overridden dependencies

### Data Fixtures
- `draft_application` - A draft application record
- `submitted_application` - A submitted application record
- `application_with_files` - An application with linked files
- `active_form_schema` - An active form schema
- `sample_form_schema` - Sample schema data

**Using fixtures:**
```python
async def test_example(db_session: AsyncSession, draft_application: Application):
    # Your test code here
    # db_session and draft_application are automatically provided
    pass
```

## Mocking External Dependencies

For services that interact with external APIs (like file-storage-service):

```python
from unittest.mock import patch, AsyncMock

@patch('app.services.zip_service.httpx.AsyncClient')
async def test_with_mocked_http(mock_client_class):
    mock_client = AsyncMock()
    mock_client_class.return_value.__aenter__.return_value = mock_client
    
    # Configure mock responses
    mock_client.get.return_value.json.return_value = {'key': 'value'}
    
    # Run your test
```

## Code Coverage

After running tests with coverage:

1. View terminal summary:
```bash
uv run pytest --cov=app --cov-report=term-missing
```

2. Generate HTML report:
```bash
uv run pytest --cov=app --cov-report=html
open htmlcov/index.html  # macOS/Linux
```

**Coverage goals:**
- Core business logic (repositories, services): 90%+
- API endpoints: 80%+
- Overall: 75%+

## Best Practices

### 1. Test Naming
Use descriptive names that explain what is being tested:
```python
# Good
async def test_create_telegram_session_resume_existing_draft()

# Bad
async def test_session()
```

### 2. Arrange-Act-Assert Pattern
Structure tests clearly:
```python
async def test_example():
    # Arrange: Set up test data
    user_id = 123456789
    
    # Act: Perform the action
    result = await create_session(user_id)
    
    # Assert: Verify the outcome
    assert result is not None
    assert result.telegram_id == user_id
```

### 3. Test One Thing
Each test should verify one behavior:
```python
# Good
async def test_update_status()
async def test_update_comment()

# Bad
async def test_update_everything()
```

### 4. Use Fixtures for Setup
Don't repeat setup code:
```python
# Good
async def test_with_fixture(draft_application):
    result = await repo.get_by_uuid(draft_application.id)

# Bad
async def test_without_fixture():
    app = Application(...)
    db.add(app)
    await db.commit()
    result = await repo.get_by_uuid(app.id)
```

### 5. Test Error Cases
Don't just test the happy path:
```python
async def test_get_application_not_found():
    result = await repo.get_by_uuid(uuid.uuid4())
    assert result is None

async def test_submit_already_submitted_application():
    response = await client.post(f'/applications/{uuid}/submit')
    assert response.status_code == 400
```

## Troubleshooting

### Tests hang or timeout
- Check for missing `await` keywords
- Verify async fixtures are properly defined
- Ensure database connections are closed

### Import errors
- Verify `pythonpath = src` is set in `pytest.ini`
- Check that `__init__.py` files exist in all packages

### Database errors
- Ensure SQLite is installed for `aiosqlite`
- Check that migrations are compatible with SQLite
- Verify test database is properly cleaned up

### Mocking issues
- Use `AsyncMock` for async functions
- Patch at the point of use, not definition
- Reset mocks between tests if needed

## CI/CD Integration

To run tests in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd services/api_service
    uv sync
    uv run pytest --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Adding New Tests

When adding new features:

1. Write tests first (TDD approach)
2. Test both success and failure cases
3. Mock external dependencies
4. Update fixtures if needed
5. Maintain coverage above 75%

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)