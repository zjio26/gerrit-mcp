"""Account-related MCP tools for Gerrit."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context

from gerrit_mcp.gerrit_client import GerritAPIError, GerritClient
from gerrit_mcp.tools import _format_result, _handle_error


def _client(ctx: Context) -> GerritClient:
    """Retrieve the GerritClient from the MCP server's lifespan context."""
    return ctx.request_context.lifespan_context["client"]


def register_account_tools(mcp) -> None:
    """Register all account-related MCP tools on the given FastMCP instance."""

    @mcp.tool()
    async def gerrit_get_self_account(ctx: Context) -> str:
        """Get the authenticated user's account information."""
        client = _client(ctx)
        try:
            result = await client.get_self_account()
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_get_account(
        ctx: Context,
        account_id: str,
    ) -> str:
        """Get an account by name or ID.

        Args:
            account_id: Username, email, or account ID
        """
        client = _client(ctx)
        try:
            result = await client.get_account(account_id)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)
