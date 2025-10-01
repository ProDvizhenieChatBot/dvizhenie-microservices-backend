from functools import cached_property

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str = 'Charity MVP - API Service'

    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    FILE_STORAGE_SERVICE_URL: str
    S3_PUBLIC_URL: str
    S3_ENDPOINT_URL: str

    @computed_field
    @cached_property
    def database_url(self) -> str:
        return (
            'postgresql+asyncpg://'
            f'{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}'
        )

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
