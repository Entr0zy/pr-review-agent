"""Render a ReviewResult for different surfaces (markdown, JSON, GitHub, GitLab, Slack)."""
from .formatters import (
    to_github_review,
    to_gitlab_discussions,
    to_json,
    to_markdown,
    to_slack_blocks,
)

__all__ = [
    "to_markdown",
    "to_json",
    "to_github_review",
    "to_gitlab_discussions",
    "to_slack_blocks",
]
