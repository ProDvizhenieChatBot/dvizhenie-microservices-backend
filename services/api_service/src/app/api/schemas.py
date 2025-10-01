from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.db import get_async_session
from app.models.db_models import FormSchema
from app.schemas.forms import FormSchemaUpload


router = APIRouter()
admin_router = APIRouter()


@router.get('/schema/active', response_model=dict)
async def get_active_form_schema(session: AsyncSession = Depends(get_async_session)):
    """
    Returns the currently active form schema from the database.
    This is used by the frontend to render the application form.
    """
    query = select(FormSchema).where(FormSchema.is_active.is_(True))
    result = await session.execute(query)
    active_schema = result.scalar_one_or_none()

    if not active_schema:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='No active form schema found in the database.',
        )

    return active_schema.schema_data


@admin_router.post(
    '/admin/forms/schema',
    status_code=status.HTTP_201_CREATED,
    summary='(Admin) Upload a new form schema and set it as active',
)
async def upload_new_schema(
    schema_upload: FormSchemaUpload,
    session: AsyncSession = Depends(get_async_session),
):
    """
    (Admin) Uploads a new version of the form schema.

    This endpoint performs two actions in a single transaction:
    1. Sets `is_active = false` for all existing schemas.
    2. Creates a new schema record with the provided data and sets `is_active = true`.
    """
    async with session.begin():
        await session.execute(update(FormSchema).values(is_active=False))

        new_schema = FormSchema(
            version=schema_upload.version,
            schema_data=schema_upload.schema_data,
            is_active=True,
        )
        session.add(new_schema)

    return {'message': f'Schema version {schema_upload.version} has been uploaded and activated.'}
