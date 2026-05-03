"""Application configuration via pydantic-settings / environment variables."""

from __future__ import annotations

import functools

from pydantic import model_validator
from pydantic_settings import BaseSettings

_VALID_TRANSPORTS = {"stdio", "sse", "streamable-http"}


class Settings(BaseSettings):
    """Gerrit MCP configuration loaded from environment variables."""

    GERRIT_URL: str
    GERRIT_USERNAME: str
    GERRIT_PASSWORD: str
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    GERRIT_VERIFY_SSL: bool = True
    GERRIT_TIMEOUT: int = 30
    MCP_READONLY: bool = False
    MCP_TRANSPORT: str = "streamable-http"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @model_validator(mode="after")
    def _validate_transport(self) -> Settings:
        if self.MCP_TRANSPORT not in _VALID_TRANSPORTS:
            raise ValueError(
                f"MCP_TRANSPORT must be one of {_VALID_TRANSPORTS}, "
                f"got {self.MCP_TRANSPORT!r}"
            )
        return self


@functools.lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
