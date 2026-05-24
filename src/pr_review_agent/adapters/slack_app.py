"""Slack adapter — TARGET: Slack Agent Builder Challenge (deadline Jul 13, UK eligible).

Plan:
  1. A Slack app (Bolt) listens for a shortcut / slash command referencing a PR.
  2. It uses MCP server integration (a qualifying technology) to fetch the diff.
  3. `PRReviewer.review_diff` produces findings, posted back to the channel as a
     threaded message + an architecture-diagram-friendly summary block.

This is a stub: fill in once a Slack developer sandbox exists.
"""
from __future__ import annotations


def handle_review_command(pr_url: str) -> dict:
    raise NotImplementedError(
        "Build with Slack Bolt; reuse PRReviewer for the core review step."
    )
