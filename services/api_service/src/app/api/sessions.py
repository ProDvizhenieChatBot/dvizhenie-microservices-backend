import logging

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import AppRepo
from app.schemas.applications import ApplicationStatusResponse
from app.schemas.sessions import SessionResponse, TelegramSessionRequest


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/telegram', response_model=SessionResponse)
async def create_or_resume_telegram_session(
    request: TelegramSessionRequest,
    repo: AppRepo,
):
    """
    This endpoint is called by the Bot Service when a user starts a conversation.

    It performs the following logic:
    1. Searches for an existing application in 'draft' status for the given telegram_id.
    2. If found, it returns the UUID of that application.
    3. If not found, it creates a new draft application, links it to the telegram_id,
       and returns the new UUID.
    """
    telegram_id = request.telegram_id
    existing_application = await repo.get_draft_by_telegram_id(telegram_id)

    if existing_application:
        logger.info(
            f'Resuming session for telegram_id={telegram_id} '
            f'with application_uuid={existing_application.id}'
        )
        return {'application_uuid': str(existing_application.id)}

    new_application = await repo.create_for_telegram_user(telegram_id)
    return {'application_uuid': str(new_application.id)}


@router.post('/web', response_model=SessionResponse)
async def create_web_session(repo: AppRepo):
    """
    Creates a new session for a user starting from the web widget.

    This endpoint creates a new draft application without a telegram_id
    and returns its unique UUID. The frontend is responsible for storing
    this UUID (e.g., in a cookie) to manage the session.
    """
    new_application = await repo.create_for_web_user()
    return {'application_uuid': str(new_application.id)}


@router.get('/telegram/status', response_model=ApplicationStatusResponse)
async def get_telegram_application_status(
    repo: AppRepo,
    telegram_id: int = Query(..., description='The Telegram ID of the user.'),
):
    """
    Gets the status of the most recent application for a given Telegram user.
    """
    application = await repo.get_latest_by_telegram_id(telegram_id)

    if application is None:
        logger.warning(f'No application found for telegram_id={telegram_id}')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No application found for Telegram user {telegram_id}',
        )

    logger.info(f'Status for telegram_id={telegram_id} is "{application.status}"')
    return {'status': application.status}
