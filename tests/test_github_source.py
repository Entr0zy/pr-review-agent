import pytest

from pr_review_agent.sources.github import _build_request, parse_pr_url


def test_parse_pr_url():
    assert parse_pr_url("https://github.com/calcom/cal.com/pull/29350") == (
        "calcom",
        "cal.com",
        29350,
    )


def test_parse_pr_url_rejects_non_pr():
    with pytest.raises(ValueError):
        parse_pr_url("https://github.com/calcom/cal.com/issues/5756")


def test_build_request_url_and_headers():
    req = _build_request("o", "r", 5, token="abc")
    assert req.full_url == "https://api.github.com/repos/o/r/pulls/5"
    assert req.headers["Accept"] == "application/vnd.github.v3.diff"
    assert req.headers["Authorization"] == "Bearer abc"


def test_build_request_without_token(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    req = _build_request("o", "r", 5)
    assert "Authorization" not in req.headers
