from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://datashield:datashield@localhost:5432/datashield"
    cors_origins: list[str] = ["http://localhost:5173"]
    upload_dir: str = "storage/uploads"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", case_sensitive=False)


settings = Settings()
