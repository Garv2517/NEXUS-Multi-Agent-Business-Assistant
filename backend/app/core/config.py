import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Nexus API"
    APP_ENV: str = "development"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    DATABASE_PATH: str = str(BASE_DIR / "data" / "nexus.db")
    ANALYTICS_DATABASE_PATH: str = "data/nexus_analytics.db"

    # Microsoft Foundry / Azure AI configurations (Phase B4)
    FOUNDRY_PROJECT_ENDPOINT: Optional[str] = ""
    FOUNDRY_MODEL: Optional[str] = "gpt-5-mini"
    ORCHESTRATION_MODE: str = "local"
    FOUNDRY_FALLBACK_TO_LOCAL: bool = True
    FOUNDRY_ROUTING_TIMEOUT_SECONDS: float = 15.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_database_path(self) -> str:
        """Resolves database path relative to BASE_DIR if relative."""
        if self.DATABASE_PATH == ":memory:":
            return ":memory:"
        p = Path(self.DATABASE_PATH)
        if not p.is_absolute():
            return str((BASE_DIR / p).resolve())
        return str(p.resolve())

    def get_analytics_database_path(self) -> str:
        """Resolves analytics database path relative to BASE_DIR if relative."""
        if self.ANALYTICS_DATABASE_PATH == ":memory:":
            return ":memory:"
        p = Path(self.ANALYTICS_DATABASE_PATH)
        if not p.is_absolute():
            candidate = (BASE_DIR / p).resolve()
            if candidate.exists():
                return str(candidate)
            candidate_root = (BASE_DIR.parent / p).resolve()
            if candidate_root.exists():
                return str(candidate_root)
            return str(candidate)
        return str(p.resolve())


settings = Settings()
