"""High-level agent entrypoint: review a pull/merge request by URL.

Auto-detects the forge from the URL, fetches the diff, and runs the engine.
This is the single function the platform adapters (Google Cloud Agent Builder,
Slack, GitHub App) call.
"""
from __future__ import annotations

from collections.abc import Callable

from .llm.base import LLMClient
from .models import ReviewResult
from .reviewer import PRReviewer


def _auto_fetch(url: str, token: str | None) -> str:
    if "/-/merge_requests/" in url:
        from .sources.gitlab import fetch_mr_diff_from_url
        return fetch_mr_diff_from_url(url, token=token)
    from .sources.github import fetch_pr_diff_from_url
    return fetch_pr_diff_from_url(url, token=token)


def review_url(
    url: str,
    llm: LLMClient,
    *,
    token: str | None = None,
    fetcher: Callable[[str, str | None], str] | None = None,
    batch_char_budget: int | None = None,
) -> ReviewResult:
    """Fetch the diff for ``url`` and review it.

    Args:
        url: a GitHub PR or GitLab MR URL.
        llm: the LLM backend to review with.
        token: forge API token (else read from env by the source).
        fetcher: override the diff fetcher (used in tests).
        batch_char_budget: see :class:`PRReviewer`.
    """
    diff_text = (fetcher or _auto_fetch)(url, token)
    return PRReviewer(llm, batch_char_budget=batch_char_budget).review_diff(diff_text)
