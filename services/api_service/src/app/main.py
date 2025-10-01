import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import sessions
from app.api.applications import (
    admin_router as applications_admin_router,
    router as applications_public_router,
)
from app.api.schemas import admin_router as schemas_admin_router, router as schemas_public_router
from app.core.config import settings
from app.core.initial_data import seed_initial_form_schema


logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    - On startup, it seeds the initial form schema if the database is empty.
    """
    logger.info('API Service is starting up...')
    await seed_initial_form_schema()
    yield
    logger.info('API Service is shutting down...')


app = FastAPI(title=settings.APP_TITLE, lifespan=lifespan)

app.include_router(applications_public_router, prefix='/api/v1/applications', tags=['Applications'])
app.include_router(
    applications_admin_router, prefix='/api/v1/admin/applications', tags=['Admin: Applications']
)
app.include_router(schemas_public_router, prefix='/api/v1/forms', tags=['Forms'])
app.include_router(schemas_admin_router, prefix='/api/v1', tags=['Admin: Forms'])
app.include_router(sessions.router, prefix='/api/v1/sessions', tags=['Sessions'])


@app.get('/api/v1/health')
def health_check():
    return {'status': 'ok', 'service': 'API Service'}
