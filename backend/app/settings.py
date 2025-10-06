from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "KiloCode Standalone"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    openai_api_key: str
    model: str = "gpt-4o-mini"
    allow_execute: bool = False  # set True only when sandboxed

    class Config:
        env_file = ".env"

settings = Settings()