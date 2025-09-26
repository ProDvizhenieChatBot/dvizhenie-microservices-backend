from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.core.db import Base


class Application(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default='new', nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# TODO: Define other necessary SQLAlchemy models here
# - User (for Mini App/Web Widget users)
# - AdminUser (for admin panel users)
# - Comment
# - FormSchema (to store schemas in the DB)
# - ApplicationFileLink (to link applications to file_ids from the file service)
