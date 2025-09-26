import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

# TODO: This logic should be replaced. The schema must be fetched from the database
# from a 'FormSchema' table. This file is a temporary solution.
STATIC_SCHEMA_PATH = Path(__file__).parent.parent / 'static' / 'form_schema.json'

@router.get('/schema/active')
def get_active_form_schema():
    """
    Returns the currently active form schema from the database.
    (Currently returns a static file as a placeholder).
    """
    if not STATIC_SCHEMA_PATH.is_file():
        raise HTTPException(status_code=500, detail='Form schema file not found.')

    with open(STATIC_SCHEMA_PATH, encoding='utf-8') as f:
        return json.load(f)

# TODO: Implement Admin endpoints for schema management
# GET /admin/forms/schemas
# PUT /admin/forms/schemas/{id}
# POST /admin/forms/schemas/{id}/activate