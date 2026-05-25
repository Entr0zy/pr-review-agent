import json

from pr_review_agent.models import Finding, ReviewResult, Severity
from pr_review_agent.output import (
    to_github_review,
    to_gitlab_discussions,
    to_json,
    to_markdown,
    to_slack_blocks,
)


def _result() -> ReviewResult:
    return ReviewResult(
        findings=[
            Finding(file="a.py", severity=Severity.CRITICAL, title="Secret",
                    detail="hardcoded", line=3, suggestion="use env"),
            Finding(file="b.py", severity=Severity.LOW, title="print", line=None),
        ],
        summary="2 finding(s): 1 critical, 1 low",
    )


def test_markdown_includes_severity_and_location():
    md = to_markdown(_result())
    assert "[CRITICAL]" in md
    assert "`a.py`:3" in md


def test_markdown_empty():
    assert "No issues found" in to_markdown(ReviewResult(summary="No issues found."))


def test_json_roundtrips():
    data = json.loads(to_json(_result()))
    assert len(data["findings"]) == 2
    assert data["has_blocking"] is True


def test_github_review_payload():
    payload = to_github_review(_result())
    assert payload["event"] == "REQUEST_CHANGES"
    # only the line-bearing finding becomes an inline comment
    assert len(payload["comments"]) == 1
    assert payload["comments"][0]["path"] == "a.py"
    assert payload["comments"][0]["line"] == 3


def test_gitlab_discussions_payload():
    items = to_gitlab_discussions(_result())
    assert len(items) == 2
    assert items[0]["position"]["new_line"] == 3
    assert "position" not in items[1]  # no line -> general comment


def test_slack_blocks_have_header():
    blocks = to_slack_blocks(_result())
    assert blocks[0]["type"] == "header"
