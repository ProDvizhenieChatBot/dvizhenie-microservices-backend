from fastapi import FastAPI

from app.api import files
from app.core.config import settings


app = FastAPI(title=settings.APP_TITLE)

app.include_router(files.router, prefix='/api/v1/files', tags=['Files'])


@app.get('/api/v1/health')
def health_check():
    return {'status': 'ok', 'service': 'File Storage Service'}
