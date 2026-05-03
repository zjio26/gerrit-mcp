"""Gerrit MCP server — FastMCP app with configurable transport.

Exposes Gerrit code review capabilities as MCP tools.
Supports stdio, sse, and streamable-http transports.
Uses stateless_http=True and json_response=True (streamable-http only)
for horizontal scalability behind an MCP gateway.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from gerrit_mcp.config import get_settings
from gerrit_mcp.gerrit_client import GerritClient
from gerrit_mcp.tools.accounts import register_account_tools
from gerrit_mcp.tools.changes import register_change_tools
from gerrit_mcp.tools.projects import register_project_tools

logger = logging.getLogger(__name__)


@asynccontextmanager
async def _lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage the GerritClient lifecycle.

    Creates a client on startup and closes it on shutdown, yielding it
    as the lifespan context so tools can access it via
    ``ctx.request_context.lifespan_context["client"]``.
    """
    settings = get_settings()
    client = GerritClient(settings)
    logger.info(
        "GerritClient created for %s (user=%s)",
        settings.GERRIT_URL,
        settings.GERRIT_USERNAME,
    )
    logger.info("Readonly mode: %s", settings.MCP_READONLY)
    logger.info("Transport mode: %s", settings.MCP_TRANSPORT)
    try:
        yield {"client": client}
    finally:
        await client.close()
        logger.info("GerritClient closed")


def create_app() -> FastMCP:
    """Build and return the configured FastMCP application."""
    settings = get_settings()
    transport = settings.MCP_TRANSPORT

    kwargs: dict = dict(
        name="gerrit-mcp",
        instructions=(
            "Gerrit MCP service — exposes Gerrit code review capabilities as MCP tools. "
            "Use the available tools to query changes, review code, manage projects, "
            "and interact with the Gerrit code review system."
        ),
        lifespan=_lifespan,
    )

    if transport in ("sse", "streamable-http"):
        kwargs["host"] = settings.HOST
        kwargs["port"] = settings.PORT

    if transport == "streamable-http":
        kwargs["streamable_http_path"] = "/mcp"
        kwargs["stateless_http"] = True
        kwargs["json_response"] = True

    mcp = FastMCP(**kwargs)

    # Register all tool groups
    register_change_tools(mcp)
    register_project_tools(mcp)
    register_account_tools(mcp)

    return mcp


def main() -> None:
    """Entry point for the gerrit-mcp command."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app = create_app()
    settings = get_settings()
    logger.info("Starting gerrit-mcp with transport=%s", settings.MCP_TRANSPORT)
    app.run(transport=settings.MCP_TRANSPORT)


if __name__ == "__main__":
    main()
