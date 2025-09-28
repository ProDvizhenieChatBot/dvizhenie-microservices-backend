# services/file_storage_service/src/app/api/files.py
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from types_aiobotocore_s3.client import S3Client

from app.core.config import settings
from app.s3_client import get_s3_client
from app.schemas.files import FileUploadResponse


router = APIRouter()


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


@router.get('/{file_id}/download-link')
async def get_download_link(file_id: str):
    """
    Generates a temporary, pre-signed URL for downloading a file.
    """
    # TODO: Implement MinIO S3 client logic to generate a pre-signed URL.
    return {
        'message': 'TODO: Implement pre-signed URL generation',
        'download_url': f'https://minio.example.com/files/{file_id}?signature=...&expires=...',
    }
