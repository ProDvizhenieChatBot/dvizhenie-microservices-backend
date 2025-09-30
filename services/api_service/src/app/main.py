from fastapi import FastAPI

from app.api import applications, auth, schemas, sessions
from app.core.config import settings


app = FastAPI(title=settings.APP_TITLE)

# Register API routers
app.include_router(applications.router, prefix='/api/v1/applications', tags=['Applications'])
app.include_router(schemas.router, prefix='/api/v1/forms', tags=['Forms'])
app.include_router(sessions.router, prefix='/api/v1/sessions', tags=['Sessions'])
app.include_router(auth.router, prefix='/api/v1/auth', tags=['Authentication'])


@app.get('/api/v1/health')
def health_check():
    return {'status': 'ok', 'service': 'API Service'}
