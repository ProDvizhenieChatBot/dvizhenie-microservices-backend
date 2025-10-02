"""
Pytest configuration and fixtures for Bot Service tests.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import types


@pytest.fixture
def mock_message() -> MagicMock:
    """Provides a mock Aiogram Message object with a mocked `answer` method."""
    message = MagicMock(spec=types.Message)
    message.answer = AsyncMock()
    message.from_user = MagicMock(spec=types.User)
    message.from_user.id = 123456789
    return message
