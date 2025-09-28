# services/api_service/src/app/models/db_models.py
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class Application(Base):
    __tablename__ = 'applications'

    # The `Mapped` type tells the type checker what the Python type is.
    # The `mapped_column` function tells SQLAlchemy how to map it to the database.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String, default='new', nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# TODO: Define other necessary SQLAlchemy models here
# - User (for Mini App/Web Widget users)
# - AdminUser (for admin panel users)
# - Comment
# - FormSchema (to store schemas in the DB)
# - ApplicationFileLink (to link applications to file_ids from the file service)
