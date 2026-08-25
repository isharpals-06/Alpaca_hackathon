from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Alpaca Paper Trading
    ALPACA_API_KEY: str = ""
    ALPACA_SECRET_KEY: str = ""
    ALPACA_BASE_URL: str = "https://paper-api.alpaca.markets"
    
    # Supabase (Managed Cloud)
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # OpenRouter API & LLM Models
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    DEFAULT_LLM_MODEL: str = "deepseek/deepseek-chat"
    
    # Risk Parameters (Defaults)
    MAX_POSITION_SIZE_PCT: float = 0.10      # Max 10% portfolio value per position
    MAX_OPTIONS_EXPOSURE_PCT: float = 0.40   # Max 40% portfolio collateral in options
    MAX_SECTOR_CONCENTRATION_PCT: float = 0.20 # Max 20% exposure in single underlying/sector
    
    # Environment
    ENV: str = "dev"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
