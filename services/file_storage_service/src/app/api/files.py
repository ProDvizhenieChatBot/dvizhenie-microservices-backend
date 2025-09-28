# services/file_storage_service/src/app/api/files.py
import uuid
from pathlib import Path

from botocore.exceptions import ClientError
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from types_aiobotocore_s3.client import S3Client

from app.core.config import settings
from app.s3_client import get_s3_client
from app.schemas.files import FileDownloadResponse, FileUploadResponse


router = APIRouter()

URL_EXPIRATION_SECONDS = 3600  # 1 hour


@router.post('/', response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile, s3_client: S3Client = Depends(get_s3_client)):
    """
    Accepts a file, saves it to MinIO, and returns a unique file_id.
    """
    file_extension = Path(file.filename).suffix if file.filename else ''
    file_id = f'{uuid.uuid4()}{file_extension}'
    bucket_name = settings.MINIO_BUCKET_NAME

    try:
        await s3_client.upload_fileobj(file.file, bucket_name, file_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to upload file to S3: {e}',
        ) from e

    return {
        'file_id': file_id,
        'filename': file.filename,
        'content_type': file.content_type,
    }


@router.get(
    '/{file_id}/download-link',
    response_model=FileDownloadResponse,
    summary='Get a temporary download link for a file',
)
async def get_download_link(file_id: str, s3_client: S3Client = Depends(get_s3_client)):
    """
    Generates a temporary, pre-signed URL for downloading a file from MinIO.
    """
    bucket_name = settings.MINIO_BUCKET_NAME

    try:
        await s3_client.head_object(Bucket=bucket_name, Key=file_id)

        internal_url = await s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': bucket_name, 'Key': file_id},
            ExpiresIn=URL_EXPIRATION_SECONDS,
        )

        public_url = internal_url.replace(settings.S3_ENDPOINT_URL, settings.S3_PUBLIC_URL)
        return {'download_url': public_url}

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '404':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'File with id "{file_id}" not found.',
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An S3 error occurred: {e}',
        ) from e
