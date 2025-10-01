from pydantic import BaseModel


class TelegramSessionRequest(BaseModel):
    telegram_id: int


class SessionResponse(BaseModel):
    application_uuid: str
