"""Stavrophora-specific settings for the Crossref API client."""

from functools import lru_cache

from bibliofabric.config import BaseApiSettings
from pydantic import Field
from pydantic_settings import SettingsConfigDict

from .constants import DEFAULT_USER_AGENT


class StavrophoraSettings(BaseApiSettings):
    """Crossref-specific settings.

    Inherits all generic API client settings from BaseApiSettings and adds
    Crossref-specific configuration.

    Settings are loaded from environment variables (prefixed with 'STAVROPHORA_')
    or .env/secrets.env files.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", "secrets.env"),
        env_file_encoding="utf-8",
        env_prefix="STAVROPHORA_",
        extra="ignore",
        case_sensitive=False,
        arbitrary_types_allowed=True,
    )

    user_agent: str = Field(
        default=DEFAULT_USER_AGENT,
        description="User-Agent header for requests",
    )

    mailto: str | None = Field(
        default=None,
        description="Contact email; puts requests in the Crossref polite pool",
    )


@lru_cache
def get_settings() -> StavrophoraSettings:
    """Provide cached access to application settings."""
    return StavrophoraSettings()
