"""Fetch a merge request's unified diff from the GitLab REST API.

Stdlib-only. Uses the ``raw_diffs`` endpoint, which returns git-style unified
diff text that :mod:`pr_review_agent.diff_parser` understands. Works for
gitlab.com and self-hosted instances. Token via ``GITLAB_TOKEN`` or arg.
"""
from __future__ import annotations

import os
import re
import urllib.parse
import urllib.request

# Captures host, project path (may contain subgroups), and MR iid.
_MR_URL_RE = re.compile(r"(?:https?://)?([^/]+)/(.+?)/-/merge_requests/(\d+)")


def parse_mr_url(url: str) -> tuple[str, str, int]:
    """Parse ``https://gitlab.com/group/proj/-/merge_requests/5`` -> (host, 'group/proj', 5)."""
    match = _MR_URL_RE.search(url)
    if not match:
        raise ValueError(f"Not a GitLab merge request URL: {url!r}")
    return match.group(1), match.group(2), int(match.group(3))


def _build_request(host: str, project_path: str, iid: int,
                   token: str | None = None) -> urllib.request.Request:
    encoded = urllib.parse.quote(project_path, safe="")
    api = f"https://{host}/api/v4/projects/{encoded}/merge_requests/{iid}/raw_diffs"
    headers = {"User-Agent": "pr-review-agent"}
    token = token or os.environ.get("GITLAB_TOKEN")
    if token:
        headers["PRIVATE-TOKEN"] = token
    return urllib.request.Request(api, headers=headers)


def fetch_mr_diff(host: str, project_path: str, iid: int,
                  token: str | None = None, timeout: int = 30) -> str:
    request = _build_request(host, project_path, iid, token)
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return response.read().decode("utf-8", "replace")


def fetch_mr_diff_from_url(url: str, token: str | None = None) -> str:
    return fetch_mr_diff(*parse_mr_url(url), token=token)
