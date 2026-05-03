"""Change-related MCP tools for Gerrit."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context

from gerrit_mcp.gerrit_client import GerritAPIError, GerritClient
from gerrit_mcp.tools import _format_result, _handle_error, _require_writable


def _client(ctx: Context) -> GerritClient:
    """Retrieve the GerritClient from the MCP server's lifespan context."""
    return ctx.request_context.lifespan_context["client"]


def register_change_tools(mcp) -> None:
    """Register all change-related MCP tools on the given FastMCP instance."""

    @mcp.tool()
    async def gerrit_query_changes(
        ctx: Context,
        query: str,
        limit: int = 25,
        offset: int | None = None,
    ) -> str:
        """Query changes using Gerrit query syntax.

        Args:
            query: Gerrit query expression (e.g. "status:open project:my-project")
            limit: Maximum number of results to return (default 25)
            offset: Number of results to skip
        """
        client = _client(ctx)
        try:
            result = await client.query_changes(query, limit=limit, offset=offset)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_get_change(
        ctx: Context,
        change_id: str,
        options: list[str] | None = None,
    ) -> str:
        """Get detailed info for a specific change.

        Args:
            change_id: Change ID or change number
            options: Detail options like CURRENT_REVISION, CURRENT_COMMIT, MESSAGES, LABELS
        """
        client = _client(ctx)
        try:
            result = await client.get_change(change_id, options=options)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_get_change_detail(
        ctx: Context,
        change_id: str,
    ) -> str:
        """Get change detail with all revision info.

        Args:
            change_id: Change ID or change number
        """
        client = _client(ctx)
        try:
            result = await client.get_change_detail(change_id)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_review_change(
        ctx: Context,
        change_id: str,
        revision_id: str = "current",
        message: str | None = None,
        labels: dict[str, int] | None = None,
    ) -> str:
        """Review a change (score + message).

        Args:
            change_id: Change ID or change number
            revision_id: Revision ID (default "current")
            message: Review comment message
            labels: Review labels, e.g. {"Code-Review": 2}
        """
        if (err := _require_writable()) is not None:
            return err
        client = _client(ctx)
        try:
            result = await client.review_change(
                change_id,
                revision_id,
                message=message,
                labels=labels,
            )
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_submit_change(
        ctx: Context,
        change_id: str,
    ) -> str:
        """Submit a change for merging.

        Args:
            change_id: Change ID or change number
        """
        if (err := _require_writable()) is not None:
            return err
        client = _client(ctx)
        try:
            result = await client.submit_change(change_id)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_abandon_change(
        ctx: Context,
        change_id: str,
        message: str | None = None,
    ) -> str:
        """Abandon a change.

        Args:
            change_id: Change ID or change number
            message: Reason for abandoning
        """
        if (err := _require_writable()) is not None:
            return err
        client = _client(ctx)
        try:
            result = await client.abandon_change(change_id, message=message)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_restore_change(
        ctx: Context,
        change_id: str,
        message: str | None = None,
    ) -> str:
        """Restore an abandoned change.

        Args:
            change_id: Change ID or change number
            message: Optional message
        """
        if (err := _require_writable()) is not None:
            return err
        client = _client(ctx)
        try:
            result = await client.restore_change(change_id, message=message)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_rebase_change(
        ctx: Context,
        change_id: str,
    ) -> str:
        """Rebase a change.

        Args:
            change_id: Change ID or change number
        """
        if (err := _require_writable()) is not None:
            return err
        client = _client(ctx)
        try:
            result = await client.rebase_change(change_id)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_get_change_comments(
        ctx: Context,
        change_id: str,
    ) -> str:
        """List comments on a change.

        Args:
            change_id: Change ID or change number
        """
        client = _client(ctx)
        try:
            result = await client.get_change_comments(change_id)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_set_topic(
        ctx: Context,
        change_id: str,
        topic: str,
    ) -> str:
        """Set topic on a change.

        Args:
            change_id: Change ID or change number
            topic: Topic to set
        """
        if (err := _require_writable()) is not None:
            return err
        client = _client(ctx)
        try:
            result = await client.set_topic(change_id, topic)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_add_reviewer(
        ctx: Context,
        change_id: str,
        reviewer: str,
    ) -> str:
        """Add reviewer to a change.

        Args:
            change_id: Change ID or change number
            reviewer: Account name, email, or ID to add as reviewer
        """
        if (err := _require_writable()) is not None:
            return err
        client = _client(ctx)
        try:
            result = await client.add_reviewer(change_id, reviewer)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_list_reviewers(
        ctx: Context,
        change_id: str,
    ) -> str:
        """List reviewers on a change.

        Args:
            change_id: Change ID or change number
        """
        client = _client(ctx)
        try:
            result = await client.list_reviewers(change_id)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)
