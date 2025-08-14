"""Application configuration and settings.

Uses Pydantic Settings to read environment variables with sensible defaults.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Typed application settings container."""
    model_dir: str = os.getenv("MODEL_DIR", "app/model")
    demographics_csv: str = os.getenv("DEMOGRAPHICS_CSV", "app/data/zipcode_demographics.csv")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    model_name: str = os.getenv("MODEL_NAME", "KNeighborsRegressor")

    # API configs
    api_version: str = "1.0.0"
    api_major_version: str = "/api/v1"
    api_project_name: str = "Housing Price API"
    

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


