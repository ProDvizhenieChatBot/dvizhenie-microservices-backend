"""
Unit tests for the bot command handlers.
"""

from unittest.mock import AsyncMock, patch

import pytest
from aiogram import types

from app.bot.handlers import (
    DEFAULT_ERROR_MESSAGE,
    STATUS_MESSAGES,
    form_handler,
    start_handler,
    status_handler,
)
from app.core.config import settings


@pytest.mark.asyncio
async def test_start_handler(mock_message):
    """Test that the /start command sends the correct welcome message."""
    await start_handler(mock_message)

    mock_message.answer.assert_awaited_once()
    # Check that the message contains key phrases
    call_args = mock_message.answer.call_args[0][0]
    assert 'Здравствуйте!' in call_args
    assert '/form' in call_args
    assert '/status' in call_args


@pytest.mark.asyncio
class TestFormHandler:
    """Test suite for the /form command handler."""

    @patch('app.bot.handlers.api_client', new_callable=AsyncMock)
    async def test_form_handler_success(self, mock_api_client, mock_message):
        """Test successful session creation and Mini App button reply."""
        mock_api_client.create_telegram_session.return_value = 'test-uuid-123'

        await form_handler(mock_message)

        mock_api_client.create_telegram_session.assert_awaited_once_with(
            telegram_id=mock_message.from_user.id
        )

        mock_message.answer.assert_awaited_once()
        args, kwargs = mock_message.answer.call_args
        assert 'Чтобы подать заявку' in args[0]
        assert 'reply_markup' in kwargs

        keyboard = kwargs['reply_markup']
        assert isinstance(keyboard, types.InlineKeyboardMarkup)
        button = keyboard.inline_keyboard[0][0]
        assert button.text == '✍️ Заполнить анкету'
        assert isinstance(button.web_app, types.WebAppInfo)
        assert button.web_app.url == f'{settings.MINI_APP_URL}?token=test-uuid-123'

    @patch('app.bot.handlers.api_client', new_callable=AsyncMock)
    async def test_form_handler_api_failure(self, mock_api_client, mock_message):
        """Test error message reply when the API client fails."""
        mock_api_client.create_telegram_session.return_value = None

        await form_handler(mock_message)

        mock_api_client.create_telegram_session.assert_awaited_once()
        mock_message.answer.assert_awaited_once_with(
            'Произошла ошибка при создании сессии. Пожалуйста, попробуйте позже.'
        )


@pytest.mark.asyncio
class TestStatusHandler:
    """Test suite for the /status command handler."""

    @pytest.mark.parametrize('status_key', STATUS_MESSAGES.keys())
    @patch('app.bot.handlers.api_client', new_callable=AsyncMock)
    async def test_status_handler_success(self, mock_api_client, mock_message, status_key):
        """Test correct status message is sent for each possible status."""
        mock_api_client.get_telegram_application_status.return_value = status_key

        await status_handler(mock_message)

        mock_api_client.get_telegram_application_status.assert_awaited_once_with(
            telegram_id=mock_message.from_user.id
        )
        expected_message = STATUS_MESSAGES[status_key]
        mock_message.answer.assert_awaited_once_with(expected_message)

    @patch('app.bot.handlers.api_client', new_callable=AsyncMock)
    async def test_status_handler_api_failure(self, mock_api_client, mock_message):
        """Test default error message is sent when the API client fails."""
        mock_api_client.get_telegram_application_status.return_value = None

        await status_handler(mock_message)

        mock_api_client.get_telegram_application_status.assert_awaited_once()
        mock_message.answer.assert_awaited_once_with(DEFAULT_ERROR_MESSAGE)
