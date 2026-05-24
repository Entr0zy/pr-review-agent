"""Fetch a pull request's unified diff from the GitHub REST API.

Stdlib-only (urllib). Uses the ``application/vnd.github.v3.diff`` media type,
which returns the raw unified diff directly. A token (``GITHUB_TOKEN`` env var or
explicit arg) is optional for public repos but recommended for rate limits /
private repos.
"""
from __future__ import annotations

import os
import re
import urllib.request

_PR_URL_RE = re.compile(r"github\.com/([^/\s]+)/([^/\s]+)/pull/(\d+)")
_API = "https://api.github.com/repos/{owner}/{repo}/pulls/{number}"


def parse_pr_url(url: str) -> tuple[str, str, int]:
    """Parse ``https://github.com/owner/repo/pull/123`` into (owner, repo, 123)."""
    match = _PR_URL_RE.search(url)
    if not match:
        raise ValueError(f"Not a GitHub PR URL: {url!r}")
    return match.group(1), match.group(2), int(match.group(3))


def _build_request(owner: str, repo: str, number: int,
                   token: str | None = None) -> urllib.request.Request:
    headers = {
        "Accept": "application/vnd.github.v3.diff",
        "User-Agent": "pr-review-agent",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = token or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(
        _API.format(owner=owner, repo=repo, number=number), headers=headers
    )


def fetch_pr_diff(owner: str, repo: str, number: int,
                  token: str | None = None, timeout: int = 30) -> str:
    """Return the raw unified diff for a pull request."""
    request = _build_request(owner, repo, number, token)
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.read().decode("utf-8", "replace")


def fetch_pr_diff_from_url(url: str, token: str | None = None) -> str:
    return fetch_pr_diff(*parse_pr_url(url), token=token)
