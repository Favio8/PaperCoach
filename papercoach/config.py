from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the local PaperCoach service."""

    model_config = SettingsConfigDict(env_prefix="PAPERCOACH_", env_file=".env", extra="ignore")

    data_dir: Path = Field(default=Path("data"))
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    llm_provider: str = Field(default="local")
    openai_api_key: str | None = Field(default=None)
    openai_base_url: str = Field(default="https://api.openai.com/v1")
    openai_model: str = Field(default="gpt-4.1-mini")
    deepseek_api_key: str | None = Field(default=None)
    deepseek_base_url: str = Field(default="https://api.deepseek.com")
    deepseek_model: str = Field(default="deepseek-v4-flash")
    llm_timeout_seconds: float = Field(default=45.0)

    @property
    def papers_dir(self) -> Path:
        return self.data_dir / "papers"

    @property
    def sessions_dir(self) -> Path:
        return self.data_dir / "sessions"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"
