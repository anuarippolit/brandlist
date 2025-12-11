from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent  # = backend/system

class Settings(BaseSettings):
    # OPENAI_API_KEY: str
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),  # ищет именно в system/.env
        env_file_encoding="utf-8"
    )

settings = Settings()
