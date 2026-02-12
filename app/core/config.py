from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Remar Chatbot"
    API_VERSION: str = "v1"
    LOG_LEVEL: str = "INFO"
    LOG_JSON: str = "0"

    # MegaAPI
    MEGA_API_URL: str
    MEGA_API_INSTANCE_KEY: str
    MEGA_API_TOKEN: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Google Sheets (opcional)
    GOOGLE_SHEETS_SPREADSHEET_ID: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_SHEETS_CREDENTIALS_JSON: Optional[str] = None

    # Admin panel (simples)
    ADMIN_USER: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
