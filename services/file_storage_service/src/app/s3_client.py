import logging

import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings


logger = logging.getLogger(__name__)

session = aioboto3.Session(
    aws_access_key_id=settings.MINIO_ROOT_USER,
    aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
)


async def get_s3_client():
    """
    Dependency to get an S3 client.

    This context manager will create an S3 client and properly close it
    when it's no longer needed.
    """
    async with session.client('s3', endpoint_url=settings.S3_ENDPOINT_URL) as s3:
        yield s3


async def create_bucket_if_not_exists():
    """
    Checks if the configured S3 bucket exists and creates it if it doesn't.
    This function is intended to be called on application startup.
    """
    bucket_name = settings.MINIO_BUCKET_NAME
    logger.info(f'Checking if bucket "{bucket_name}" exists...')

    try:
        async for s3 in get_s3_client():
            try:
                await s3.head_bucket(Bucket=bucket_name)
                logger.info(f'Bucket "{bucket_name}" already exists.')
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if error_code == '404':
                    logger.info(f'Bucket "{bucket_name}" not found. Creating it...')
                    await s3.create_bucket(Bucket=bucket_name)
                    logger.info(f'Bucket "{bucket_name}" created successfully.')
                else:
                    logger.error(f'Unexpected S3 error: {e}', exc_info=True)
                    raise
    except Exception as e:
        logger.error(f'Failed to check or create bucket: {e}', exc_info=True)
        raise
