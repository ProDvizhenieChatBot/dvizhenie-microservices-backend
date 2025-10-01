import logging
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.db_models import Application, ApplicationFile
from app.schemas.applications import (
    ApplicationAdminUpdate,
    ApplicationStatus,
    ApplicationUpdate,
    FileLinkRequest,
)


logger = logging.getLogger(__name__)


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_uuid(
        self, application_uuid: UUID, with_files: bool = False
    ) -> Application | None:
        query = select(Application).where(Application.id == application_uuid)
        if with_files:
            query = query.options(selectinload(Application.files))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_draft_by_telegram_id(self, telegram_id: int) -> Application | None:
        query = select(Application).where(
            Application.telegram_id == telegram_id,
            Application.status == ApplicationStatus.DRAFT.value,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_latest_by_telegram_id(self, telegram_id: int) -> Application | None:
        query = (
            select(Application)
            .where(Application.telegram_id == telegram_id)
            .order_by(desc(Application.created_at))
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        status: ApplicationStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Application]:
        query = (
            select(Application)
            .options(selectinload(Application.files))
            .order_by(Application.created_at)
        )
        if status:
            query = query.where(Application.status == status.value)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create_for_telegram_user(self, telegram_id: int) -> Application:
        new_application = Application(
            telegram_id=telegram_id, status=ApplicationStatus.DRAFT.value, data={}
        )
        self.session.add(new_application)
        await self.session.commit()
        await self.session.refresh(new_application)
        logger.info(
            f'Created new session for telegram_id={telegram_id} '
            f'with new application_uuid={new_application.id}'
        )
        return new_application

    async def create_for_web_user(self) -> Application:
        new_application = Application(
            telegram_id=None, status=ApplicationStatus.DRAFT.value, data={}
        )
        self.session.add(new_application)
        await self.session.commit()
        await self.session.refresh(new_application)
        logger.info(f'Created new web session with application_uuid={new_application.id}')
        return new_application

    async def update_progress(
        self, db_application: Application, update_data: ApplicationUpdate
    ) -> Application:
        db_application.data = update_data.data
        self.session.add(db_application)
        await self.session.commit()
        await self.session.refresh(db_application)
        return db_application

    async def update_admin_details(
        self, db_application: Application, update_data: ApplicationAdminUpdate
    ) -> Application:
        if update_data.status is not None:
            db_application.status = update_data.status.value
        if update_data.admin_comment is not None:
            db_application.admin_comment = update_data.admin_comment
        self.session.add(db_application)
        await self.session.commit()
        await self.session.refresh(db_application, attribute_names=['files'])
        return db_application

    async def submit_application(self, db_application: Application) -> Application:
        db_application.status = ApplicationStatus.NEW.value
        self.session.add(db_application)
        await self.session.commit()
        return db_application

    async def link_file(self, application_uuid: UUID, file_link: FileLinkRequest) -> None:
        new_file_link = ApplicationFile(
            application_id=application_uuid,
            file_id=file_link.file_id,
            original_filename=file_link.original_filename,
            form_field_id=file_link.form_field_id,
        )
        self.session.add(new_file_link)
        await self.session.commit()
