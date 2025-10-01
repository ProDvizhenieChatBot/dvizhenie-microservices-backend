import json
import logging
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.future import select

from app.core.db import AsyncSessionLocal
from app.models.db_models import FormSchema


logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent.parent / 'static'
FORM_SCHEMA_PATH = STATIC_DIR / 'form_schema.json'


async def seed_initial_form_schema():
    """
    Checks if the form_schemas table is empty and, if so, populates it
    with the default schema from form_schema.json.
    """
    logger.info('Checking if initial form schema needs to be seeded...')

    async with AsyncSessionLocal() as session, session.begin():
        result = await session.execute(select(func.count()).select_from(FormSchema))
        count = result.scalar_one()

        if count > 0:
            logger.info('Form schemas table is not empty. Skipping initial data seeding.')
            return

        logger.info('Form schemas table is empty. Seeding initial data...')

        if not FORM_SCHEMA_PATH.is_file():
            logger.error(f'Initial form schema file not found at: {FORM_SCHEMA_PATH}')
            raise FileNotFoundError(f'Could not find {FORM_SCHEMA_PATH}')

        with open(FORM_SCHEMA_PATH, encoding='utf-8') as f:
            schema_data = json.load(f)

        initial_schema = FormSchema(
            version=schema_data.get('version', '1.0'),
            schema_data=schema_data,
            is_active=True,
        )

        session.add(initial_schema)
        await session.commit()

        logger.info(f'Successfully seeded initial form schema version {initial_schema.version}.')
