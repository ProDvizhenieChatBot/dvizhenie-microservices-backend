# services/api_service/src/app/api/sessions.py
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.db import get_async_session
from app.models.db_models import Application
from app.schemas.applications import ApplicationStatus, ApplicationStatusResponse


router = APIRouter()
logger = logging.getLogger(__name__)


# --- Pydantic Schemas for this endpoint ---
class TelegramSessionRequest(BaseModel):
    telegram_id: int


class SessionResponse(BaseModel):
    application_uuid: str


# --- Endpoint Implementation ---
@router.post('/telegram', response_model=SessionResponse)
async def create_or_resume_telegram_session(
    request: TelegramSessionRequest,
    session: AsyncSession = Depends(get_async_session),
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

    # 1. Look for an existing draft application
    query = select(Application).where(
        Application.telegram_id == telegram_id,
        Application.status == ApplicationStatus.DRAFT.value,
    )
    result = await session.execute(query)
    existing_application = result.scalar_one_or_none()

    if existing_application:
        # 2. If found, return its UUID
        logger.info(
            f'Resuming session for telegram_id={telegram_id} '
            f'with application_uuid={existing_application.id}'
        )
        return {'application_uuid': str(existing_application.id)}

    # 3. If not found, create a new one
    new_application = Application(
        telegram_id=telegram_id,
        status=ApplicationStatus.DRAFT.value,
        data={},
    )
    session.add(new_application)
    await session.commit()
    await session.refresh(new_application)

    logger.info(
        f'Created new session for telegram_id={telegram_id} '
        f'with new application_uuid={new_application.id}'
    )
    return {'application_uuid': str(new_application.id)}


@router.post('/web', response_model=SessionResponse)
async def create_web_session(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Creates a new session for a user starting from the web widget.

    This endpoint creates a new draft application without a telegram_id
    and returns its unique UUID. The frontend is responsible for storing
    this UUID (e.g., in a cookie) to manage the session.
    """
    new_application = Application(
        telegram_id=None,  # Explicitly set to None for web sessions
        status=ApplicationStatus.DRAFT.value,
        data={},
    )
    session.add(new_application)
    await session.commit()
    await session.refresh(new_application)

    logger.info(f'Created new web session with application_uuid={new_application.id}')
    return {'application_uuid': str(new_application.id)}


@router.get('/telegram/status', response_model=ApplicationStatusResponse)
async def get_telegram_application_status(
    telegram_id: int = Query(..., description='The Telegram ID of the user.'),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Gets the status of the most recent application for a given Telegram user.
    """
    query = (
        select(Application.status)
        .where(Application.telegram_id == telegram_id)
        .order_by(desc(Application.created_at))
        .limit(1)
    )
    result = await session.execute(query)
    application_status = result.scalar_one_or_none()

    if application_status is None:
        logger.warning(f'No application found for telegram_id={telegram_id}')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No application found for Telegram user {telegram_id}',
        )

    logger.info(f'Status for telegram_id={telegram_id} is "{application_status}"')
    return {'status': application_status}
