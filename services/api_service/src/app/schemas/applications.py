from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    """
    Represents the input schema for creating an application.
    For a draft, no input is needed from the client.
    """

    pass


class ApplicationResponse(BaseModel):
    """
    Represents the response schema for a newly created application.
    """

    id: int = Field(..., description='The unique identifier of the application')
    status: str = Field(..., description='The current status of the application')

    model_config = ConfigDict(from_attributes=True)
