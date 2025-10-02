from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.db_models import FormSchema
from app.schemas.forms import FormSchemaUpload


class FormSchemaRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_schema(self) -> FormSchema | None:
        """
        Retrieves the currently active form schema from the database.
        """
        query = select(FormSchema).where(FormSchema.is_active.is_(True))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_and_set_active_schema(self, schema_upload: FormSchemaUpload) -> FormSchema:
        """
        Creates a new schema, sets it as active, and deactivates all others.
        This method assumes it's operating within an existing transaction.
        """
        await self.session.execute(update(FormSchema).values(is_active=False))

        new_schema = FormSchema(
            version=schema_upload.version,
            schema_data=schema_upload.schema_data,
            is_active=True,
        )
        self.session.add(new_schema)

        await self.session.flush()

        await self.session.refresh(new_schema)

        return new_schema
