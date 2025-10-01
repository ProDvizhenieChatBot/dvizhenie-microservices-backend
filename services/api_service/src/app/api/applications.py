# services/api_service/src/app/api/applications.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.db import get_async_session
from app.models.db_models import Application, ApplicationFile
from app.schemas.applications import (
    ApplicationAdmin,
    ApplicationAdminUpdate,
    ApplicationPublic,
    ApplicationStatus,
    ApplicationStatusResponse,
    ApplicationUpdate,
    FileLinkRequest,
)
from app.services.export_service import generate_xlsx_export
from app.services.zip_service import create_documents_zip_archive


router = APIRouter()
admin_router = APIRouter()

# --- Admin Endpoints ---


@admin_router.get(
    '/',
    response_model=list[ApplicationAdmin],
    summary='(Admin) Get a list of all applications',
)
async def get_all_applications(
    status: ApplicationStatus | None = Query(None, description='Filter by application status'),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
):
    """
    (Admin) Retrieves a list of applications, with optional filtering and pagination.
    """
    query = (
        select(Application)
        .options(selectinload(Application.files))
        .order_by(Application.created_at)
    )

    if status:
        query = query.where(Application.status == status.value)

    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    return result.scalars().all()


@admin_router.get(
    '/export',
    response_class=StreamingResponse,
    summary='(Admin) Export applications to an XLSX file',
)
async def export_applications_to_xlsx(session: AsyncSession = Depends(get_async_session)):
    """
    (Admin) Fetches all applications from the database, flattens the data,
    and returns it as an XLSX file.
    """
    query = select(Application).options(selectinload(Application.files))
    result = await session.execute(query)
    applications = result.scalars().all()

    xlsx_buffer = generate_xlsx_export(applications)

    return StreamingResponse(
        content=xlsx_buffer,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment; filename="applications_export.xlsx"',
        },
    )


@admin_router.get(
    '/{application_uuid}/download-documents',
    response_class=StreamingResponse,
    summary='(Admin) Download all documents for an application as a ZIP archive',
)
async def download_documents_as_zip(
    application_uuid: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    (Admin) Generates and streams a ZIP file containing all documents
    attached to a specific application.
    """
    query = (
        select(Application)
        .where(Application.id == application_uuid)
        .options(selectinload(Application.files))
    )
    result = await session.execute(query)
    db_application = result.scalar_one_or_none()

    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )
    if not db_application.files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No documents found for this application.',
        )

    zip_buffer = await create_documents_zip_archive(app=db_application, settings=settings)

    zip_filename = f'application_docs_{application_uuid}.zip'
    return StreamingResponse(
        content=zip_buffer,
        media_type='application/zip',
        headers={'Content-Disposition': f'attachment; filename="{zip_filename}"'},
    )


@admin_router.get(
    '/{application_uuid}',
    response_model=ApplicationAdmin,
    summary='(Admin) Get detailed information for a single application',
)
async def get_application_details_admin(
    application_uuid: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    (Admin) Retrieves full details for a specific application, including linked files.
    """
    query = (
        select(Application)
        .where(Application.id == application_uuid)
        .options(selectinload(Application.files))
    )
    result = await session.execute(query)
    db_application = result.scalar_one_or_none()

    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )
    return db_application


@admin_router.patch(
    '/{application_uuid}',
    response_model=ApplicationAdmin,
    summary='(Admin) Update application status or add a comment',
)
async def update_application_admin(
    application_uuid: UUID,
    update_data: ApplicationAdminUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    (Admin) Updates an application's status or internal admin comment.
    """
    query = select(Application).where(Application.id == application_uuid)
    result = await session.execute(query)
    db_application = result.scalar_one_or_none()

    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )

    if update_data.status is not None:
        db_application.status = update_data.status.value
    if update_data.admin_comment is not None:
        db_application.admin_comment = update_data.admin_comment

    session.add(db_application)
    await session.commit()

    await session.refresh(db_application, attribute_names=['files'])

    return db_application


# --- Public Endpoints for Mini App ---


@router.get(
    '/{application_uuid}/public/status',
    response_model=ApplicationStatusResponse,
    summary='Get the status of a specific application',
)
async def get_application_status_public(
    application_uuid: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Retrieves the current status of a single application by its UUID.
    This is a public endpoint for the web-widget to check status.
    """
    query = select(Application.status).where(Application.id == application_uuid)
    result = await session.execute(query)
    application_status = result.scalar_one_or_none()

    if application_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )
    return {'status': application_status}


@router.get(
    '/{application_uuid}/public',
    response_model=ApplicationPublic,
    summary='Get application data for filling',
)
async def get_application_data_public(
    application_uuid: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Retrieves the current data for an application, used by the Mini App to resume.
    """
    db_application = await session.get(Application, application_uuid)
    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )
    return db_application


@router.patch(
    '/{application_uuid}/public',
    response_model=ApplicationPublic,
    summary='Save application progress',
)
async def save_application_progress(
    application_uuid: UUID,
    application_in: ApplicationUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Saves the user's progress from the Mini App.
    """
    db_application = await session.get(Application, application_uuid)
    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )

    if db_application.status != ApplicationStatus.DRAFT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Can only update applications in draft status.',
        )

    db_application.data = application_in.data
    session.add(db_application)
    await session.commit()
    await session.refresh(db_application)
    return db_application


@router.post(
    '/{application_uuid}/files',
    status_code=status.HTTP_201_CREATED,
    summary='Link an uploaded file to the application',
)
async def link_file_to_application(
    application_uuid: UUID,
    file_link: FileLinkRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    After a file is uploaded to the file-storage-service, the Mini App calls
    this endpoint to create a record linking the file_id to the application.
    """
    db_application = await session.get(Application, application_uuid)
    if not db_application:
        raise HTTPException(status_code=404, detail='Application not found')

    new_file_link = ApplicationFile(
        application_id=application_uuid,
        file_id=file_link.file_id,
        original_filename=file_link.original_filename,
        form_field_id=file_link.form_field_id,
    )
    session.add(new_file_link)
    await session.commit()
    return {'message': 'File linked successfully'}


@router.post(
    '/{application_uuid}/submit',
    status_code=status.HTTP_200_OK,
    summary='Submit the application for review',
)
async def submit_application(
    application_uuid: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Finalizes the application, changing its status from 'draft' to 'new'.
    """
    db_application = await session.get(Application, application_uuid)
    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )

    if db_application.status != ApplicationStatus.DRAFT.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Application has already been submitted.',
        )

    db_application.status = ApplicationStatus.NEW.value
    session.add(db_application)
    await session.commit()
    return {'message': 'Application submitted successfully'}
