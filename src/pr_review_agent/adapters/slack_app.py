"""Slack adapter — Slack Agent Builder Challenge ($42k, deadline Jul 13).

A Slack app where ``/review <github-or-gitlab-url>`` makes the agent fetch the
diff, review it, and post Block Kit findings back to the channel. Qualifies
under the challenge's "MCP server integration" technology (the review fetch can
run through the GitHub/GitLab MCP).

``slack-bolt`` is an optional dependency ([slack] extra), imported lazily so the
core engine and its tests don't require it. ``parse_command`` and
``build_review_blocks`` are pure and unit-tested without the SDK.
"""
from __future__ import annotations

import os
import re
from collections.abc import Callable

from ..models import ReviewResult
from ..output import to_slack_blocks

_URL_RE = re.compile(r"https?://\S+")


def parse_command(text: str | None) -> str | None:
    """Extract a PR/MR URL from slash-command text (handles Slack's ``<url|label>``)."""
    if not text:
        return None
    match = _URL_RE.search(text)
    if not match:
        return None
    return match.group(0).split("|")[0].strip("<>")


def build_review_blocks(url: str | None,
                        reviewer: Callable[[str], ReviewResult]) -> list[dict]:
    """Run ``reviewer`` on ``url`` and render Slack Block Kit blocks."""
    if not url:
        return [{
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Usage: `/review <github-or-gitlab-url>`"},
        }]
    return to_slack_blocks(reviewer(url))


def _default_reviewer(url: str) -> ReviewResult:
    from ..agent import review_url
    from ..llm.gemini import GeminiClient
    model = os.getenv("PR_REVIEW_MODEL", "gemini-2.5-flash")
    return review_url(url, GeminiClient(model=model))


def create_app(reviewer: Callable[[str], ReviewResult] | None = None):
    """Create the Slack Bolt app.

    Requires the [slack] extra and Slack env vars (SLACK_BOT_TOKEN,
    SLACK_SIGNING_SECRET).
    """
    try:
        from slack_bolt import App
    except ImportError as exc:  # pragma: no cover - optional extra
        raise ImportError(
            "slack-bolt is not installed. Run: pip install 'pr-review-agent[slack]'"
        ) from exc

    review = reviewer or _default_reviewer
    app = App()

    @app.command("/review")
    def _handle_review(ack, command, say):  # pragma: no cover - needs Slack runtime
        ack()
        url = parse_command(command.get("text", ""))
        say(blocks=build_review_blocks(url, review))

    return app


def main() -> None:  # pragma: no cover - needs Slack runtime
    """Run the app in Socket Mode (needs SLACK_APP_TOKEN)."""
    from slack_bolt.adapter.socket_mode import SocketModeHandler

    SocketModeHandler(create_app(), os.environ["SLACK_APP_TOKEN"]).start()


if __name__ == "__main__":  # pragma: no cover
    main()
