import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.db import Base


class Application(Base):
    __tablename__ = 'applications'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=False,
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String, default='draft', nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    admin_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    files: Mapped[list['ApplicationFile']] = relationship(
        back_populates='application', cascade='all, delete-orphan'
    )


class ApplicationFile(Base):
    __tablename__ = 'application_files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False
    )
    file_id: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    form_field_id: Mapped[str] = mapped_column(
        String, nullable=False, comment='ID of the field in the form schema this file belongs to'
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    application: Mapped['Application'] = relationship(back_populates='files')


class FormSchema(Base):
    """Stores versions of the application form schema."""

    __tablename__ = 'form_schemas'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String, nullable=False)
    schema_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, server_default='false', nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
