from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./denuncias.db"
    ai_provider: str = "mock"
    google_api_key: str = ""
    google_model: str = "gemini-3.5-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    lm_studio_base_url: str = "http://localhost:1234/v1"
    lm_studio_model: str = "local-model"
    assistant_behavior: str = ""
    assistant_muletilla: str = ""
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
