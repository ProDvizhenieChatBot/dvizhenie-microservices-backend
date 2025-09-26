from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_TITLE: str = 'Charity MVP - File Storage Service'

    # TODO: Add MinIO connection settings
    # MINIO_ENDPOINT: str
    # MINIO_ACCESS_KEY: str
    # MINIO_SECRET_KEY: str
    # MINIO_BUCKET: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()