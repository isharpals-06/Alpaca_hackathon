from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ALPACA_API_KEY: str = ""
    ALPACA_SECRET_KEY: str = ""
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    LLM_API_KEY: str = ""
    ENV: str = "dev"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
