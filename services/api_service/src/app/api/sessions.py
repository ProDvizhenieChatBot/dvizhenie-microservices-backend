import uuid

from fastapi import APIRouter

router = APIRouter()

@router.post('/telegram')
async def create_telegram_session():
    """
    TODO: This endpoint should be called by the Bot Service.
    It should verify the telegram_user_id, create a new application draft
    if one doesn't exist, and return a unique resume_token.
    """
    # Placeholder logic
    resume_token = str(uuid.uuid4())
    return {'resume_token': resume_token}


@router.post('/web')
async def create_web_session():
    """
    TODO: Implement "Magic Link" logic for web widget users.
    It should accept an email, generate a resume_token, and send the link.
    """
    return {'message': 'TODO: Implement web session creation'}