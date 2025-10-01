from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import FormRepo
from app.schemas.forms import FormSchemaUpload


router = APIRouter()
admin_router = APIRouter()


@router.get('/schema/active', response_model=dict)
async def get_active_form_schema(repo: FormRepo):
    """
    Returns the currently active form schema from the database.
    This is used by the frontend to render the application form.
    """
    active_schema = await repo.get_active_schema()

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
async def upload_new_schema(schema_upload: FormSchemaUpload, repo: FormRepo):
    """
    (Admin) Uploads a new version of the form schema.

    This endpoint performs two actions in a single transaction:
    1. Sets `is_active = false` for all existing schemas.
    2. Creates a new schema record with the provided data and sets `is_active = true`.
    """
    new_schema = await repo.create_and_set_active_schema(schema_upload)
    return {'message': f'Schema version {new_schema.version} has been uploaded and activated.'}
