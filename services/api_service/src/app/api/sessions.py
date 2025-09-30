from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.db import get_async_session
from app.models.db_models import Application
from app.schemas.applications import ApplicationStatus


router = APIRouter()


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

    return {'application_uuid': str(new_application.id)}
