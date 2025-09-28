from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_TITLE: str = 'Charity MVP - File Storage Service'

    # MinIO/S3 connection settings
    S3_ENDPOINT_URL: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_NAME: str

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
