from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.dependencies import AppRepo
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


@admin_router.get(
    '/',
    response_model=list[ApplicationAdmin],
    summary='(Admin) Get a list of all applications',
)
async def get_all_applications(
    repo: AppRepo,
    status: ApplicationStatus | None = Query(None, description='Filter by application status'),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    (Admin) Retrieves a list of applications, with optional filtering and pagination.
    """
    return await repo.get_all(status=status, limit=limit, offset=offset)


@admin_router.get(
    '/export',
    response_class=StreamingResponse,
    summary='(Admin) Export applications to an XLSX file',
)
async def export_applications_to_xlsx(repo: AppRepo):
    """
    (Admin) Fetches all applications from the database, flattens the data,
    and returns it as an XLSX file.
    """
    applications = await repo.get_all(limit=10000)  # A large limit to get all applications
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
    repo: AppRepo,
):
    """
    (Admin) Generates and streams a ZIP file containing all documents
    attached to a specific application.
    """
    db_application = await repo.get_by_uuid(application_uuid, with_files=True)

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
    repo: AppRepo,
):
    """
    (Admin) Retrieves full details for a specific application, including linked files.
    """
    db_application = await repo.get_by_uuid(application_uuid, with_files=True)

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
    repo: AppRepo,
):
    """
    (Admin) Updates an application's status or internal admin comment.
    """
    db_application = await repo.get_by_uuid(application_uuid)

    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )

    return await repo.update_admin_details(db_application, update_data)


@router.get(
    '/{application_uuid}/public/status',
    response_model=ApplicationStatusResponse,
    summary='Get the status of a specific application',
)
async def get_application_status_public(
    application_uuid: UUID,
    repo: AppRepo,
):
    """
    Retrieves the current status of a single application by its UUID.
    This is a public endpoint for the web-widget to check status.
    """
    db_application = await repo.get_by_uuid(application_uuid)

    if db_application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Application with id {application_uuid} not found',
        )
    return {'status': db_application.status}


@router.get(
    '/{application_uuid}/public',
    response_model=ApplicationPublic,
    summary='Get application data for filling',
)
async def get_application_data_public(
    application_uuid: UUID,
    repo: AppRepo,
):
    """
    Retrieves the current data for an application, used by the Mini App to resume.
    """
    db_application = await repo.get_by_uuid(application_uuid)
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
    repo: AppRepo,
):
    """
    Saves the user's progress from the Mini App.
    """
    db_application = await repo.get_by_uuid(application_uuid)
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

    return await repo.update_progress(db_application, application_in)


@router.post(
    '/{application_uuid}/files',
    status_code=status.HTTP_201_CREATED,
    summary='Link an uploaded file to the application',
)
async def link_file_to_application(
    application_uuid: UUID,
    file_link: FileLinkRequest,
    repo: AppRepo,
):
    """
    After a file is uploaded to the file-storage-service, the Mini App calls
    this endpoint to create a record linking the file_id to the application.
    """
    db_application = await repo.get_by_uuid(application_uuid)
    if not db_application:
        raise HTTPException(status_code=404, detail='Application not found')

    await repo.link_file(application_uuid, file_link)
    return {'message': 'File linked successfully'}


@router.post(
    '/{application_uuid}/submit',
    status_code=status.HTTP_200_OK,
    summary='Submit the application for review',
)
async def submit_application(
    application_uuid: UUID,
    repo: AppRepo,
):
    """
    Finalizes the application, changing its status from 'draft' to 'new'.
    """
    db_application = await repo.get_by_uuid(application_uuid)
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

    await repo.submit_application(db_application)
    return {'message': 'Application submitted successfully'}
