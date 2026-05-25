"""GitHub App adapter — product/portfolio lane (GitHub Marketplace).

A GitHub App subscribes to ``pull_request`` webhooks; on open/synchronize it
fetches the diff, runs the engine, and posts a review via
:func:`pr_review_agent.output.to_github_review`.

This module provides the stdlib, fully-testable pieces (signature verification,
payload parsing, event gating). The HTTP server / posting wiring is added when
deploying the App.
"""
from __future__ import annotations

import hashlib
import hmac

# Webhook actions worth reviewing.
_REVIEW_ACTIONS = {"opened", "synchronize", "reopened", "ready_for_review"}


def verify_signature(payload_body: bytes, secret: str, signature_header: str | None) -> bool:
    """Validate the ``X-Hub-Signature-256`` header GitHub sends with webhooks.

    Uses a constant-time comparison to avoid timing attacks.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        secret.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature_header)


def extract_pr(payload: dict) -> dict | None:
    """Pull review-relevant fields from a ``pull_request`` webhook payload."""
    pr = payload.get("pull_request")
    if not pr:
        return None
    full_name = payload.get("repository", {}).get("full_name", "")
    owner, _, repo = full_name.partition("/")
    return {
        "action": payload.get("action"),
        "owner": owner,
        "repo": repo,
        "number": pr.get("number"),
        "diff_url": pr.get("diff_url"),
        "html_url": pr.get("html_url"),
    }


def should_review(payload: dict) -> bool:
    """True if this webhook event should trigger a review."""
    return payload.get("action") in _REVIEW_ACTIONS
