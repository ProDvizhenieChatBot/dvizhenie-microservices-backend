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
    1. Calls the API service to create a session and get a resume_token.
    2. Sends a message with a button to open the Mini App.
    """
    # TODO: Handle potential errors from the API call
    token = await api_client.create_telegram_session()

    if token:
        # Append the token to the Mini App URL
        mini_app_url = f'{settings.MINI_APP_URL}?token={token}'

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
