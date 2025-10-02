import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import files
from app.core.config import settings

from .s3_client import create_bucket_if_not_exists


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_bucket_if_not_exists()
    yield


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)


app.include_router(files.router, prefix='/api/v1/files', tags=['Files'])


@app.get('/api/v1/health')
def health_check():
    return {'status': 'ok', 'service': 'File Storage Service'}
