# services/api_service/src/app/api/sessions.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.db_models import Application


router = APIRouter()


@router.post('/telegram', status_code=status.HTTP_201_CREATED)
async def create_telegram_session(session: AsyncSession = Depends(get_async_session)):
    """
    This endpoint is called by the Bot Service when a user starts a conversation.

    It performs two main actions:
    1.  Creates a new application with a 'draft' status in the database.
    2.  Returns a unique session token (currently the application ID) that the
        Mini App will use to identify and save progress for this specific user session.
    """
    # 1. Create a new draft application instance
    new_application = Application(
        status='draft',
        data={},  # Initialize with an empty JSON object for form data
    )

    # 2. Add to session, commit to DB, and refresh to get the new ID
    session.add(new_application)
    await session.commit()
    await session.refresh(new_application)

    # 3. Return the ID as a session token.
    # TODO: Replace with a secure JWT in the future.
    return {'session_token': new_application.id}


@router.post('/web')
async def create_web_session():
    """
    TODO: Implement "Magic Link" logic for web widget users.
    It should accept an email, generate a resume_token, and send the link.
    """
    return {'message': 'TODO: Implement web session creation'}
