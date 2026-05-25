from pr_review_agent.adapters.slack_app import build_review_blocks, parse_command
from pr_review_agent.models import Finding, ReviewResult, Severity


def test_parse_command_plain_url():
    assert parse_command("/review https://github.com/o/r/pull/1") == (
        "https://github.com/o/r/pull/1"
    )


def test_parse_command_slack_wrapped():
    assert parse_command("<https://gitlab.com/g/p/-/merge_requests/2>") == (
        "https://gitlab.com/g/p/-/merge_requests/2"
    )


def test_parse_command_with_label():
    assert parse_command("<https://github.com/o/r/pull/3|PR 3>") == (
        "https://github.com/o/r/pull/3"
    )


def test_parse_command_none():
    assert parse_command("") is None
    assert parse_command("no url here") is None


def test_build_review_blocks_uses_reviewer():
    def fake(url):
        assert url == "https://github.com/o/r/pull/1"
        return ReviewResult(
            findings=[Finding(file="a.py", severity=Severity.HIGH, title="X", line=1)],
            summary="1 finding(s): 1 high",
        )

    blocks = build_review_blocks("https://github.com/o/r/pull/1", fake)
    assert blocks[0]["type"] == "header"


def test_build_review_blocks_usage_when_no_url():
    blocks = build_review_blocks(None, lambda u: ReviewResult())
    assert "Usage" in blocks[0]["text"]["text"]
