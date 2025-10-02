"""
Pytest configuration and fixtures for Bot Service tests.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import types


@pytest.fixture
def mock_message() -> MagicMock:
    """Provides a mock Aiogram Message object with a mocked `answer` method."""
    # The message object itself can be a regular MagicMock
    message = MagicMock(spec=types.Message)
    # The method we await must be an AsyncMock
    message.answer = AsyncMock()
    message.from_user = MagicMock(spec=types.User)
    message.from_user.id = 123456789
    return message
