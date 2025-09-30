# services/bot_service/src/app/bot/handlers.py
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo

from app.core.config import settings
from app.internal_clients.api_client import api_client


router = Router()


@router.message(CommandStart())
async def start_handler(message: types.Message):
    """
    Handles the /start command.
    1. Gets the user's telegram_id.
    2. Calls the API service to create or resume a session and get an application_uuid.
    3. Sends a message with a button to open the Mini App, using the UUID as a token.
    """
    if not message.from_user:
        await message.answer('Не удалось определить пользователя. Пожалуйста, попробуйте еще раз.')
        return

    user_id = message.from_user.id
    application_uuid = await api_client.create_telegram_session(telegram_id=user_id)

    if application_uuid:
        # The token is now the UUID of the application
        mini_app_url = f'{settings.MINI_APP_URL}?token={application_uuid}'

        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text='✍️ Заполнить анкету',
                        web_app=WebAppInfo(url=mini_app_url),
                    )
                ]
            ]
        )
        await message.answer(
            "Здравствуйте! Это бот фонда 'Движение Жизни'.\n\n"
            'Чтобы подать заявку, нажмите на кнопку ниже, чтобы открыть анкету.',
            reply_markup=keyboard,
        )
    else:
        await message.answer('Произошла ошибка при создании сессии. Пожалуйста, попробуйте позже.')
