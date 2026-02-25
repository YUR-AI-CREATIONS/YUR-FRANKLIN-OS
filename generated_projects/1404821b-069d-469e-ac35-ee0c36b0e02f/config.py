import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./auth.db"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()