"""Async Gerrit REST API client with httpx."""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from gerrit_mcp.config import Settings, get_settings

logger = logging.getLogger(__name__)

XSSI_PREFIX = ")]}'\n"


class GerritAPIError(Exception):
    """Raised when the Gerrit API returns an error response."""

    def __init__(self, status: int, message: str, detail: Any = None) -> None:
        self.status = status
        self.message = message
        self.detail = detail
        super().__init__(f"Gerrit API error {status}: {message}")


class GerritClient:
    """Async client for the Gerrit REST API.

    Handles authentication (HTTP Basic), XSSI prefix stripping, and
    error response mapping.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        base_url = self._settings.GERRIT_URL.rstrip("/")
        self._base_url = base_url
        self._auth = httpx.BasicAuth(
            self._settings.GERRIT_USERNAME,
            self._settings.GERRIT_PASSWORD,
        )
        self._timeout = float(self._settings.GERRIT_TIMEOUT)
        self._verify_ssl = self._settings.GERRIT_VERIFY_SSL
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        """Lazily create the httpx async client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                auth=self._auth,
                base_url=self._base_url,
                timeout=httpx.Timeout(self._timeout),
                verify=self._verify_ssl,
                headers={"Accept": "application/json"},
            )
        return self._client

    @staticmethod
    def _strip_xssi(text: str) -> str:
        """Remove Gerrit's XSSI protection prefix if present."""
        if text.startswith(XSSI_PREFIX):
            return text[len(XSSI_PREFIX) :]
        return text

    @staticmethod
    def _parse_response(text: str) -> Any:
        """Parse Gerrit JSON response after stripping XSSI prefix."""
        cleaned = GerritClient._strip_xssi(text)
        cleaned = cleaned.strip()
        if not cleaned:
            return None
        return json.loads(cleaned)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
    ) -> Any:
        """Send an HTTP request to the Gerrit API and return parsed JSON.

        All paths should be relative to the base URL and start with /a/.
        """
        client = await self._ensure_client()
        url = path

        kwargs: dict[str, Any] = {}
        if params:
            # Convert list values to repeated params (e.g. o=LABELS&o=MESSAGES)
            flat_params: list[tuple[str, str]] = []
            for key, value in params.items():
                if isinstance(value, list):
                    for v in value:
                        flat_params.append((key, str(v)))
                else:
                    flat_params.append((key, str(value)))
            kwargs["params"] = flat_params

        if json_body is not None:
            kwargs["json"] = json_body

        logger.debug("Gerrit %s %s params=%s", method, url, params)

        response = await client.request(method, url, **kwargs)

        if response.status_code == 204:
            return None

        if response.status_code >= 400:
            try:
                error_body = self._parse_response(response.text)
                message = (
                    error_body.get("message", response.text)
                    if isinstance(error_body, dict)
                    else response.text
                )
            except (json.JSONDecodeError, ValueError):
                message = response.text
            raise GerritAPIError(response.status_code, message)

        if not response.text.strip():
            return None

        return self._parse_response(response.text)

    async def _get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        """Send a GET request to the Gerrit API."""
        return await self._request("GET", path, params=params)

    async def _post(
        self,
        path: str,
        *,
        json_body: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Send a POST request to the Gerrit API."""
        return await self._request("POST", path, params=params, json_body=json_body)

    async def _put(
        self,
        path: str,
        *,
        json_body: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Send a PUT request to the Gerrit API."""
        return await self._request("PUT", path, params=params, json_body=json_body)

    async def _delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Send a DELETE request to the Gerrit API."""
        return await self._request("DELETE", path, params=params)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    # ---- Change operations ----

    async def query_changes(
        self,
        query: str,
        *,
        limit: int = 25,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        """Query changes using Gerrit query syntax."""
        params: dict[str, Any] = {"q": query, "n": limit}
        if offset is not None:
            params["start"] = offset
        result = await self._get("/a/changes/", params=params)
        if result is None:
            return []
        return result

    async def get_change(
        self,
        change_id: str,
        *,
        options: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get detailed info for a specific change."""
        params: dict[str, Any] = {}
        if options:
            params["o"] = options
        return await self._get(f"/a/changes/{change_id}", params=params)

    async def get_change_detail(self, change_id: str) -> dict[str, Any]:
        """Get change detail with all revision info."""
        return await self._get(
            f"/a/changes/{change_id}/detail",
            params={"o": ["CURRENT_REVISION", "CURRENT_COMMIT", "MESSAGES", "LABELS"]},
        )

    async def review_change(
        self,
        change_id: str,
        revision_id: str,
        *,
        message: str | None = None,
        labels: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Review a change (score + message)."""
        body: dict[str, Any] = {}
        if message:
            body["message"] = message
        if labels:
            body["labels"] = labels
        return await self._post(
            f"/a/changes/{change_id}/revisions/{revision_id}/review",
            json_body=body,
        )

    async def submit_change(self, change_id: str) -> dict[str, Any]:
        """Submit a change for merging."""
        return await self._post(
            f"/a/changes/{change_id}/submit",
            json_body={},
        )

    async def abandon_change(
        self,
        change_id: str,
        *,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Abandon a change."""
        body: dict[str, Any] = {}
        if message:
            body["message"] = message
        return await self._post(
            f"/a/changes/{change_id}/abandon",
            json_body=body,
        )

    async def restore_change(
        self,
        change_id: str,
        *,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Restore an abandoned change."""
        body: dict[str, Any] = {}
        if message:
            body["message"] = message
        return await self._post(
            f"/a/changes/{change_id}/restore",
            json_body=body,
        )

    async def rebase_change(self, change_id: str) -> dict[str, Any]:
        """Rebase a change."""
        return await self._post(
            f"/a/changes/{change_id}/rebase",
            json_body={},
        )

    async def get_change_comments(self, change_id: str) -> dict[str, Any]:
        """List comments on a change."""
        return await self._get(f"/a/changes/{change_id}/comments")

    async def set_topic(
        self,
        change_id: str,
        topic: str,
    ) -> dict[str, Any]:
        """Set topic on a change."""
        return await self._put(
            f"/a/changes/{change_id}/topic",
            json_body={"topic": topic},
        )

    async def add_reviewer(
        self,
        change_id: str,
        reviewer: str,
    ) -> dict[str, Any]:
        """Add reviewer to a change."""
        return await self._post(
            f"/a/changes/{change_id}/reviewers",
            json_body={"reviewer": reviewer},
        )

    async def list_reviewers(self, change_id: str) -> list[dict[str, Any]]:
        """List reviewers on a change."""
        result = await self._get(f"/a/changes/{change_id}/reviewers")
        if result is None:
            return []
        return result

    # ---- Project operations ----

    async def list_projects(
        self,
        *,
        query: str | None = None,
        limit: int | None = None,
        type_: str | None = None,
    ) -> dict[str, Any]:
        """List visible projects."""
        params: dict[str, Any] = {}
        if query:
            params["q"] = query
        if limit is not None:
            params["n"] = limit
        if type_:
            params["type"] = type_
        return await self._get("/a/projects/", params=params)

    async def get_project(self, project_name: str) -> dict[str, Any]:
        """Get project description."""
        return await self._get(f"/a/projects/{project_name}")

    async def list_branches(
        self,
        project_name: str,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """List branches of a project."""
        params: dict[str, Any] = {}
        if limit is not None:
            params["n"] = limit
        result = await self._get(
            f"/a/projects/{project_name}/branches",
            params=params,
        )
        if result is None:
            return []
        return result

    async def list_tags(
        self,
        project_name: str,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """List tags of a project."""
        params: dict[str, Any] = {}
        if limit is not None:
            params["n"] = limit
        result = await self._get(
            f"/a/projects/{project_name}/tags",
            params=params,
        )
        if result is None:
            return []
        return result

    # ---- Account operations ----

    async def get_self_account(self) -> dict[str, Any]:
        """Get the authenticated user's account."""
        return await self._get("/a/accounts/self")

    async def get_account(self, account_id: str) -> dict[str, Any]:
        """Get an account by name or ID."""
        return await self._get(f"/a/accounts/{account_id}")
