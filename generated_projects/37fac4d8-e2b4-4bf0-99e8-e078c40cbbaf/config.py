from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Sample API"
    app_version: str = "1.0.0"
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "your-secret-key-change-in-production"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS settings
    cors_origins: list = ["*"]
    
    # API settings
    api_prefix: str = "/api/v1"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    
    class Config:
        env_file = ".env"

settings = Settings()