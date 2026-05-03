"""Project-related MCP tools for Gerrit."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import Context

from gerrit_mcp.gerrit_client import GerritAPIError, GerritClient
from gerrit_mcp.tools import _format_result, _handle_error


def _client(ctx: Context) -> GerritClient:
    """Retrieve the GerritClient from the MCP server's lifespan context."""
    return ctx.request_context.lifespan_context["client"]


def register_project_tools(mcp) -> None:
    """Register all project-related MCP tools on the given FastMCP instance."""

    @mcp.tool()
    async def gerrit_list_projects(
        ctx: Context,
        query: str | None = None,
        limit: int | None = None,
        project_type: str | None = None,
    ) -> str:
        """List visible projects.

        Args:
            query: Filter expression for project names
            limit: Maximum number of results
            project_type: Project type filter: CODE, PERMISSIONS, or ALL
        """
        client = _client(ctx)
        try:
            result = await client.list_projects(query=query, limit=limit, type_=project_type)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_get_project(
        ctx: Context,
        project_name: str,
    ) -> str:
        """Get project description.

        Args:
            project_name: Name of the project
        """
        client = _client(ctx)
        try:
            result = await client.get_project(project_name)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_list_branches(
        ctx: Context,
        project_name: str,
        limit: int | None = None,
    ) -> str:
        """List branches of a project.

        Args:
            project_name: Name of the project
            limit: Maximum number of results
        """
        client = _client(ctx)
        try:
            result = await client.list_branches(project_name, limit=limit)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)

    @mcp.tool()
    async def gerrit_list_tags(
        ctx: Context,
        project_name: str,
        limit: int | None = None,
    ) -> str:
        """List tags of a project.

        Args:
            project_name: Name of the project
            limit: Maximum number of results
        """
        client = _client(ctx)
        try:
            result = await client.list_tags(project_name, limit=limit)
            return _format_result(result)
        except GerritAPIError as exc:
            return _handle_error(exc)
