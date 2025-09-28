from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    """
    Represents the input schema for creating an application.
    For a draft, no input is needed from the client.
    """

    pass


class ApplicationUpdate(BaseModel):
    """Represents the input schema for updating application data."""

    data: dict = Field(..., description='JSON object with the application form data')


class ApplicationResponse(BaseModel):
    """
    Represents the response schema for an application.
    """

    id: int = Field(..., description='The unique identifier of the application')
    status: str = Field(..., description='The current status of the application')
    data: dict = Field(..., description='The JSON data of the application form')

    model_config = ConfigDict(from_attributes=True)
