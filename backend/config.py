from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """
    Defines the application's settings.
    Pydantic automatically reads these from environment variables
    (case-insensitive) or a .env file.
    """

    # Define your settings here with type hints
    RIOT_API_KEY: str

    # Tell Pydantic to load from a .env file
    # This replaces the need for load_dotenv()
    model_config = SettingsConfigDict(env_file=".env")


# Use lru_cache to create a "singleton" settings object.
# This function will only run Settings() once, the first time it's called.
# Subsequent calls will return the same cached instance.
@lru_cache
def get_settings():
    return Settings()
