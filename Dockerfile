FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build

COPY pyproject.toml .
COPY src/ src/

RUN uv venv /build/.venv && \
    uv pip install --no-cache -e .

# ---- Runtime stage ----
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/src/ /app/src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src

# Default configuration (override at runtime via env vars)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV MCP_TRANSPORT=streamable-http

EXPOSE 8000

CMD ["python", "-m", "gerrit_mcp"]
