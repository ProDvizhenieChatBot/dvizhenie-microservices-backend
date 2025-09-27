from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.db_models import Application
from app.schemas.applications import ApplicationCreate, ApplicationResponse


router = APIRouter()

# TODO: Implement Admin endpoints for application management
# GET /admin/applications
# GET /admin/applications/{id}
# PATCH /admin/applications/{id}

# TODO: Implement Public endpoints for application drafts and submission
# GET /applications/{token}
# PATCH /applications/{token}
# POST /applications/{token}


@router.get('/')
async def get_applications_placeholder():
    # This is a placeholder for admin functionality
    return {'message': 'TODO: Implement GET /admin/applications endpoint'}


@router.post(
    '/',
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Create a new draft application',
)
async def create_draft_application(
    # The request body is validated against ApplicationCreate, which is currently empty.
    application_in: ApplicationCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Creates a new application with a 'draft' status.

    This endpoint initializes a new application process by creating a record
    in the database. It returns the new application's ID and status.
    """
    # Create a new SQLAlchemy model instance
    new_application = Application(
        status='draft',
        data={},  # Explicitly set data to an empty JSON object
    )

    # Add it to the session and commit to the database
    session.add(new_application)
    await session.commit()
    await session.refresh(new_application)  # Refresh to get the DB-assigned ID

    return new_application
