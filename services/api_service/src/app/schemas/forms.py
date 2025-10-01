from pydantic import BaseModel


class FormSchemaUpload(BaseModel):
    version: str
    schema_data: dict
