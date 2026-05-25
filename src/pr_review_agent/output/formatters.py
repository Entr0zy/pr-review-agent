"""Pure functions that render a :class:`ReviewResult` for various surfaces.

These are shared by every adapter so posting logic stays out of the engine.
"""
from __future__ import annotations

import json

from ..models import ReviewResult


def _body(finding) -> str:
    text = f"**[{finding.severity.value.upper()}] {finding.title}**"
    if finding.detail:
        text += f"\n\n{finding.detail}"
    if finding.suggestion:
        text += f"\n\n_Suggestion:_ {finding.suggestion}"
    return text


def to_json(result: ReviewResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


def to_markdown(result: ReviewResult) -> str:
    lines = [f"## PR Review - {result.summary}", ""]
    if not result.findings:
        lines.append("No issues found.")
        return "\n".join(lines)
    for f in result.findings:
        loc = f"`{f.file}`" + (f":{f.line}" if f.line else "")
        lines.append(f"- **[{f.severity.value.upper()}]** {loc} - {f.title}")
        if f.detail:
            lines.append(f"  - {f.detail}")
        if f.suggestion:
            lines.append(f"  - _Suggestion:_ {f.suggestion}")
    return "\n".join(lines)


def to_github_review(result: ReviewResult) -> dict:
    """Payload for POST /repos/{o}/{r}/pulls/{n}/reviews."""
    comments = [
        {"path": f.file, "line": f.line, "side": "RIGHT", "body": _body(f)}
        for f in result.findings
        if f.line is not None
    ]
    event = "REQUEST_CHANGES" if result.has_blocking else "COMMENT"
    return {"event": event, "body": result.summary, "comments": comments}


def to_gitlab_discussions(result: ReviewResult) -> list[dict]:
    """List of discussion payloads for the GitLab MR discussions API."""
    out: list[dict] = []
    for f in result.findings:
        item: dict = {"body": _body(f)}
        if f.line is not None:
            item["position"] = {
                "position_type": "text",
                "new_path": f.file,
                "new_line": f.line,
            }
        out.append(item)
    return out


def to_slack_blocks(result: ReviewResult, max_blocks: int = 20) -> list[dict]:
    """Slack Block Kit blocks for posting a review into a channel."""
    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": "PR Review"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": result.summary}},
    ]
    for f in result.findings[:max_blocks]:
        loc = f.file + (f":{f.line}" if f.line else "")
        text = f"*[{f.severity.value.upper()}]* `{loc}` — {f.title}"
        if f.detail:
            text += f"\n{f.detail}"
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": text}})
    return blocks
