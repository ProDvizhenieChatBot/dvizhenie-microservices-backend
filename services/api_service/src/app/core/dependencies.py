from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.repositories.applications import ApplicationRepository
from app.repositories.forms import FormSchemaRepository


DbSession = Annotated[AsyncSession, Depends(get_async_session)]


def get_application_repo(session: DbSession) -> ApplicationRepository:
    """Provides an instance of ApplicationRepository."""
    return ApplicationRepository(session=session)


def get_form_schema_repo(session: DbSession) -> FormSchemaRepository:
    """Provides an instance of FormSchemaRepository."""
    return FormSchemaRepository(session=session)


AppRepo = Annotated[ApplicationRepository, Depends(get_application_repo)]
FormRepo = Annotated[FormSchemaRepository, Depends(get_form_schema_repo)]
