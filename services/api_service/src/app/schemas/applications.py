# services/api_service/src/app/schemas/applications.py
from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Status Enum based on openapi.yaml
class ApplicationStatus(str, Enum):
    DRAFT = 'draft'
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    REJECTED = 'rejected'


# --- Schemas for File Linking ---
class FileLinkRequest(BaseModel):
    """Schema to link an uploaded file to an application."""

    file_id: str
    original_filename: str
    form_field_id: str


class ApplicationFileResponse(BaseModel):
    """Represents a file linked to an application."""

    file_id: str
    original_filename: str
    form_field_id: str

    model_config = ConfigDict(from_attributes=True)


# --- Schemas for Application Lifecycle ---
class ApplicationCreate(BaseModel):
    """
    Input schema for creating an application.
    For a draft, no input is needed from the client.
    """

    pass


class ApplicationUpdate(BaseModel):
    """Input schema for updating application data (user saving progress)."""

    data: dict = Field(..., description='JSON object with the application form data')


class ApplicationAdminUpdate(BaseModel):
    """Input schema for admin updates (status, comment)."""

    status: ApplicationStatus | None = None
    admin_comment: str | None = Field(None, description='Internal comment from a staff member.')


# --- Response Schemas ---
class ApplicationPublic(BaseModel):
    """Represents the application data visible to the user (Mini App)."""

    id: UUID
    status: ApplicationStatus
    data: dict

    model_config = ConfigDict(from_attributes=True)


class ApplicationAdmin(BaseModel):
    """Represents the full application data visible to an administrator."""

    id: UUID
    status: ApplicationStatus
    data: dict
    admin_comment: str | None
    telegram_id: int | None
    created_at: datetime
    files: list[ApplicationFileResponse] = []

    model_config = ConfigDict(from_attributes=True)
