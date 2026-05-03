"""Gerrit MCP tools package."""

from __future__ import annotations

import json
from typing import Any

from gerrit_mcp.gerrit_client import GerritAPIError
from gerrit_mcp.config import get_settings


def _require_writable() -> str | None:
    """Return an error JSON string if readonly mode is active, else None."""
    if get_settings().MCP_READONLY:
        return json.dumps(
            {"error": True, "message": "Operation rejected: service is in readonly mode"},
            ensure_ascii=False,
        )
    return None


def _format_result(data: Any) -> str:
    """Format a result as JSON string for MCP tool response."""
    if data is None:
        return json.dumps({"status": "ok", "message": "Operation completed successfully"})
    return json.dumps(data, default=str, ensure_ascii=False)


def _handle_error(exc: GerritAPIError) -> str:
    """Format a GerritAPIError as a JSON error response."""
    return json.dumps(
        {"error": True, "status": exc.status, "message": exc.message},
        ensure_ascii=False,
    )
