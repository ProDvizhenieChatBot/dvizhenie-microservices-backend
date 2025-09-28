import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings


# The session will be reused throughout the application's lifecycle
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
    print(f'Checking if bucket "{bucket_name}" exists...')

    async for s3 in get_s3_client():
        try:
            # Check if the bucket exists by making a HeadBucket request
            await s3.head_bucket(Bucket=bucket_name)
            print(f'Bucket "{bucket_name}" already exists.')
        except ClientError as e:
            # Safely access the error code using .get() method
            error_code = e.response.get('Error', {}).get('Code')

            # If the error is a 404, the bucket does not exist
            if error_code == '404':
                print(f'Bucket "{bucket_name}" not found. Creating it...')
                try:
                    # Create the bucket
                    await s3.create_bucket(Bucket=bucket_name)
                    print(f'Bucket "{bucket_name}" created successfully.')
                except ClientError as create_error:
                    print(f'Error creating bucket: {create_error}')
                    raise
            else:
                # Re-raise other client errors
                print(f'An unexpected S3 error occurred: {e}')
                raise
