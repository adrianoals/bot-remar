from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Remar Chatbot"
    API_VERSION: str = "v1"
    
    # MegaAPI
    MEGA_API_URL: str
    MEGA_API_INSTANCE_KEY: str
    MEGA_API_TOKEN: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
