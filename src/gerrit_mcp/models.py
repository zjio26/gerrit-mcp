"""Pydantic models for Gerrit MCP request/response types."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GerritError(BaseModel):
    """Structured error returned from Gerrit API."""

    status: int
    message: str
    detail: dict[str, Any] | None = None


class ChangeInfo(BaseModel):
    """Minimal representation of a Gerrit change."""

    id: str | None = None
    number: int | None = Field(None, alias="_number")
    project: str | None = None
    branch: str | None = None
    topic: str | None = None
    subject: str | None = None
    status: str | None = None
    owner: dict[str, Any] | None = None
    created: str | None = None
    updated: str | None = None
    submit_type: str | None = None
    labels: dict[str, Any] | None = None
    messages: list[dict[str, Any]] | None = None
    current_revision: str | None = None
    revisions: dict[str, Any] | None = None

    model_config = {"populate_by_name": True, "extra": "allow"}


class ReviewInput(BaseModel):
    """Input for reviewing a change."""

    message: str | None = None
    labels: dict[str, int] | None = None


class AbandonInput(BaseModel):
    """Input for abandoning a change."""

    message: str | None = None


class RestoreInput(BaseModel):
    """Input for restoring a change."""

    message: str | None = None


class TopicInput(BaseModel):
    """Input for setting a topic on a change."""

    topic: str


class ReviewerInput(BaseModel):
    """Input for adding a reviewer to a change."""

    reviewer: str


class ProjectInfo(BaseModel):
    """Minimal representation of a Gerrit project."""

    id: str | None = None
    name: str | None = None
    description: str | None = None
    state: str | None = None
    web_links: list[dict[str, Any]] | None = None

    model_config = {"extra": "allow"}


class BranchInfo(BaseModel):
    """Minimal representation of a Gerrit branch."""

    ref: str | None = None
    revision: str | None = None
    can_delete: bool | None = None

    model_config = {"extra": "allow"}


class TagInfo(BaseModel):
    """Minimal representation of a Gerrit tag."""

    ref: str | None = None
    revision: str | None = None
    message: str | None = None
    tagger: dict[str, Any] | None = None

    model_config = {"extra": "allow"}


class AccountInfo(BaseModel):
    """Minimal representation of a Gerrit account."""

    account_id: int | None = Field(None, alias="_account_id")
    name: str | None = None
    email: str | None = None
    username: str | None = None
    avatars: list[dict[str, Any]] | None = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")
