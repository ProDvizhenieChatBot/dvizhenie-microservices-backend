import logging

from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.types import WebAppInfo

from app.core.config import settings
from app.internal_clients.api_client import api_client


router = Router()
logger = logging.getLogger(__name__)


STATUS_MESSAGES = {
    'draft': 'Ваша анкета находится в процессе заполнения. Вы можете вернуться к ней в любой момент.',  # noqa: E501
    'new': 'Ваша заявка принята и ожидает рассмотрения. Мы свяжемся с вами в ближайшее время.',
    'in_progress': 'Ваша заявка находится в обработке у специалиста фонда.',
    'completed': 'Ваша заявка успешно обработана и закрыта.',
    'rejected': 'К сожалению, по вашей заявке было принято отрицательное решение. Свяжитесь с нами для уточения деталей.',  # noqa: E501
    'not_found': 'Мы не нашли ваших заявок. Нажмите /form, чтобы начать заполнение анкеты.',
}
DEFAULT_ERROR_MESSAGE = 'Не удалось получить статус вашей заявки. Пожалуйста, попробуйте позже.'


@router.message(CommandStart())
async def start_handler(message: types.Message):
    """
    Handles the /start command by providing information about the bot.
    """
    await message.answer(
        "Здравствуйте! Это бот благотворительного фонда 'Про Движение'.\n\n"
        'Я помогу вам подать заявку на получение помощи.\n\n'
        'Используйте эти команды для навигации:\n'
        '🔹 `/form` — начать заполнение или вернуться к черновику анкеты.\n'
        '🔹 `/status` — узнать текущий статус вашей последней заявки.'
    )


@router.message(Command('form'))
async def form_handler(message: types.Message):
    """
    Handles the /form command.
    1. Gets the user's telegram_id.
    2. Calls the API service to create or resume a session and get an application_uuid.
    3. Sends a message with a button to open the Mini App, using the UUID as a token.
    """
    if not message.from_user:
        await message.answer('Не удалось определить пользователя. Пожалуйста, попробуйте еще раз.')
        return

    user_id = message.from_user.id
    logger.info(f'User {user_id} triggered /form command.')
    application_uuid = await api_client.create_telegram_session(telegram_id=user_id)

    if application_uuid:
        logger.info(f'Session created/resumed for user {user_id} with UUID: {application_uuid}')
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
            'Чтобы подать заявку, нажмите на кнопку ниже, чтобы открыть анкету.',
            reply_markup=keyboard,
        )
    else:
        logger.error(f'Failed to create a session for user {user_id}.')
        await message.answer('Произошла ошибка при создании сессии. Пожалуйста, попробуйте позже.')


@router.message(Command('status'))
async def status_handler(message: types.Message):
    """
    Handles the /status command.
    Fetches and displays the current status of the user's latest application.
    """
    if not message.from_user:
        await message.answer('Не удалось определить пользователя. Пожалуйста, попробуйте еще раз.')
        return

    user_id = message.from_user.id
    logger.info(f'User {user_id} triggered /status command.')
    status_key = await api_client.get_telegram_application_status(telegram_id=user_id)
    logger.info(f'Status for user {user_id} is "{status_key}"')

    response_text = STATUS_MESSAGES.get(str(status_key), DEFAULT_ERROR_MESSAGE)
    await message.answer(response_text)
