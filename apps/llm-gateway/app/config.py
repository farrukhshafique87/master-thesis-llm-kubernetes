from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Where requests are forwarded (the FastAPI service inside the cluster).
    UPSTREAM_URL: str = "http://fastapi-service:8010"

    # Shared secret clients must present as "Authorization: Bearer <key>".
    # No default on purpose: the gateway must not start without a real key.
    API_KEY: str = Field(min_length=16)

    REQUEST_TIMEOUT: int = 120
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
