

# Gerrit MCP

Built with [Forge](https://github.com/zjio26/forge)

A [Model Context Protocol](https://modelcontextprotocol.io/) server that bridges AI assistants with [Gerrit](https://www.gerritcodereview.com/) code review systems.

**Query changes · Review code · Manage projects — all through natural language.**

[Python 3.11+](https://www.python.org/downloads/)
[MCP](https://modelcontextprotocol.io/)
[License](LICENSE)

[中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md)



---

## Features

- **Change Management** — Query, review, submit, abandon, restore, and rebase changes
- **Project Browsing** — List projects, branches, and tags
- **Account Lookup** — Query user profiles and the authenticated self
- **Reviewer Workflow** — Add and list reviewers on changes
- **Comment Access** — Read inline comments on any change
- **Read-only Mode** — Safe deployment that blocks all write operations
- **Multi-Transport** — stdio, SSE, and Streamable HTTP out of the box

## Quick Start

### Run with uvx 

```bash
# Install uv if you haven't
# curl -LsSf https://astral.sh/uv/install.sh | sh

# Run directly from GitHub — no clone or install required
GERRIT_URL=https://gerrit.example.com \
GERRIT_USERNAME=your-username \
GERRIT_PASSWORD=your-http-password \
MCP_TRANSPORT=stdio \
uvx --from git+https://github.com/zjio26/gerrit-mcp.git gerrit-mcp
```

### Install locally

```bash
# Clone and install with uv (recommended)
git clone https://github.com/zjio26/gerrit-mcp.git
cd gerrit-mcp
uv pip install -e .

# Or using pip
pip install -e .
```

### Configure

Create a `.env` file with your Gerrit credentials:

```bash
GERRIT_URL=https://gerrit.example.com
GERRIT_USERNAME=your-username
GERRIT_PASSWORD=your-http-password
```

> Generate an HTTP password at Gerrit → Settings → HTTP Password.

### Run

```bash
# Default: Streamable HTTP on http://0.0.0.0:8000
python -m gerrit_mcp

# stdio transport (for Claude Desktop, etc.)
MCP_TRANSPORT=stdio python -m gerrit_mcp

# SSE transport
MCP_TRANSPORT=sse python -m gerrit_mcp
```

### Docker

```bash
docker build -t gerrit-mcp .
docker run --env-file .env -p 8000:8000 gerrit-mcp

# Or with a different transport
docker run --env-file .env -e MCP_TRANSPORT=stdio gerrit-mcp
```

## MCP Tools

### Changes


| Tool                         | Description                              | Write |
| ---------------------------- | ---------------------------------------- | ----- |
| `gerrit_query_changes`       | Search changes using Gerrit query syntax |       |
| `gerrit_get_change`          | Get detailed info for a specific change  |       |
| `gerrit_get_change_detail`   | Get change detail with all revision info |       |
| `gerrit_get_change_comments` | List comments on a change                |       |
| `gerrit_review_change`       | Review a change (score + message)        | **W** |
| `gerrit_submit_change`       | Submit a change for merging              | **W** |
| `gerrit_abandon_change`      | Abandon a change                         | **W** |
| `gerrit_restore_change`      | Restore an abandoned change              | **W** |
| `gerrit_rebase_change`       | Rebase a change                          | **W** |
| `gerrit_set_topic`           | Set topic on a change                    | **W** |
| `gerrit_add_reviewer`        | Add reviewer to a change                 | **W** |
| `gerrit_list_reviewers`      | List reviewers on a change               |       |


### Projects


| Tool                   | Description                | Write |
| ---------------------- | -------------------------- | ----- |
| `gerrit_list_projects` | List visible projects      |       |
| `gerrit_get_project`   | Get project description    |       |
| `gerrit_list_branches` | List branches of a project |       |
| `gerrit_list_tags`     | List tags of a project     |       |


### Accounts


| Tool                      | Description                               | Write |
| ------------------------- | ----------------------------------------- | ----- |
| `gerrit_get_self_account` | Get the authenticated user's account info |       |
| `gerrit_get_account`      | Get an account by name, email, or ID      |       |


Tools marked **W** are blocked when `MCP_READONLY=true`.

## Configuration


| Variable            | Description                                          | Default           |
| ------------------- | ---------------------------------------------------- | ----------------- |
| `GERRIT_URL`        | Gerrit server base URL                               | *required*        |
| `GERRIT_USERNAME`   | HTTP password username                               | *required*        |
| `GERRIT_PASSWORD`   | HTTP password                                        | *required*        |
| `MCP_TRANSPORT`     | Transport mode: `stdio`, `sse`, or `streamable-http` | `streamable-http` |
| `HOST`              | Server bind host (HTTP transports only)              | `0.0.0.0`         |
| `PORT`              | Server bind port (HTTP transports only)              | `8000`            |
| `MCP_READONLY`      | Block all write operations                           | `false`           |
| `GERRIT_VERIFY_SSL` | Verify SSL certificates                              | `true`            |
| `GERRIT_TIMEOUT`    | Request timeout in seconds                           | `30`              |


## Client Integration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gerrit": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/zjio26/gerrit-mcp.git", "gerrit-mcp"],
      "env": {
        "MCP_TRANSPORT": "stdio",
        "GERRIT_URL": "https://gerrit.example.com",
        "GERRIT_USERNAME": "your-username",
        "GERRIT_PASSWORD": "your-http-password"
      }
    }
  }
}
```

### MCP Gateway (Streamable HTTP)

The default `streamable-http` transport is designed for horizontal scalability behind MCP gateways. It uses `stateless_http=True` and `json_response=True` for proxy compatibility.

```bash
# Start the server
python -m gerrit_mcp
# MCP endpoint: http://localhost:8000/mcp
```

### SSE Client

```bash
MCP_TRANSPORT=sse python -m gerrit_mcp
# SSE endpoint: http://localhost:8000/sse
```

## Development

```bash
# Install with dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with verbose output
pytest -v
```

## Architecture

```
src/gerrit_mcp/
├── __init__.py
├── __main__.py          # Entry point: python -m gerrit_mcp
├── server.py            # FastMCP app, transport config, lifespan
├── config.py            # pydantic-settings, env vars
├── gerrit_client.py     # Async Gerrit REST API client (httpx)
├── models.py            # Pydantic request/response models
└── tools/
    ├── __init__.py      # Shared helpers: _format_result, _handle_error, _require_writable
    ├── changes.py       # Change-related MCP tools
    ├── projects.py      # Project-related MCP tools
    └── accounts.py      # Account-related MCP tools
```

## License

MIT