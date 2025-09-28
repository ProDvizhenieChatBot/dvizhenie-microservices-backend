from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """
    Represents the response schema after a successful file upload.
    """

    file_id: str = Field(
        ...,
        description='The unique identifier for the uploaded file.',
        examples=['a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890.pdf'],
    )
    filename: str | None = Field(
        None,
        description='The original name of the uploaded file.',
        examples=['passport_scan.pdf'],
    )
    content_type: str | None = Field(
        None,
        description='The MIME type of the file.',
        examples=['application/pdf'],
    )
