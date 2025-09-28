from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import files
from app.core.config import settings

from .s3_client import create_bucket_if_not_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup, ensure the S3 bucket exists
    await create_bucket_if_not_exists()
    yield
    # On shutdown, you can add cleanup logic here if needed


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

app.include_router(files.router, prefix='/api/v1/files', tags=['Files'])


@app.get('/api/v1/health')
def health_check():
    return {'status': 'ok', 'service': 'File Storage Service'}
