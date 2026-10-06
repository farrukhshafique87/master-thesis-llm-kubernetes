from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "LLM API"
    VERSION: str = "1.0.0"

    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:0.5b"
    REQUEST_TIMEOUT: int = 120
    LOG_LEVEL: str = "INFO"

    # --- Controlled inference parameters (experiment constants) ---
    # Fixed so that every request in every experiment does comparable work.
    LLM_TEMPERATURE: float = 0.0
    LLM_SEED: int = 42
    LLM_NUM_PREDICT: int = 64  # max generated tokens per request
    LLM_KEEP_ALIVE: str = "24h"  # keep model in memory (avoid cold-start noise)

    # Retries hide failures and add extra load; 1 (= no retry) for benchmarks.
    OLLAMA_MAX_ATTEMPTS: int = 1

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
