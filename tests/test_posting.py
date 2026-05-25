import json

import pytest

from pr_review_agent.agent import post_review_to_url
from pr_review_agent.models import Finding, ReviewResult, Severity
from pr_review_agent.sources.gitlab import _build_note_request


def test_build_note_request():
    req = _build_note_request("gitlab.com", "group/proj", 5, "hello body", token="t")
    assert req.full_url == (
        "https://gitlab.com/api/v4/projects/group%2Fproj/merge_requests/5/notes"
    )
    assert req.get_method() == "POST"
    assert req.headers["Private-token"] == "t"
    assert req.headers["Content-type"] == "application/json"
    assert json.loads(req.data.decode())["body"] == "hello body"


def test_post_review_to_url_gitlab_uses_poster():
    captured: dict = {}

    def poster(url, body, token=None):
        captured["url"] = url
        captured["body"] = body
        return {"id": 99}

    result = ReviewResult(
        findings=[Finding(file="a.py", severity=Severity.HIGH, title="Boom", line=1)],
        summary="1 finding(s): 1 high",
    )
    note = post_review_to_url(
        "https://gitlab.com/g/p/-/merge_requests/2", result, poster=poster
    )
    assert note["id"] == 99
    assert "Boom" in captured["body"]  # markdown body carries the finding


def test_post_review_to_url_github_not_supported():
    with pytest.raises(NotImplementedError):
        post_review_to_url("https://github.com/o/r/pull/1", ReviewResult())
