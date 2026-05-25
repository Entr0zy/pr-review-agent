import pytest

from pr_review_agent.sources.gitlab import _build_request, parse_mr_url


def test_parse_mr_url_with_subgroups():
    assert parse_mr_url("https://gitlab.com/gitlab-org/gitlab/-/merge_requests/12345") == (
        "gitlab.com",
        "gitlab-org/gitlab",
        12345,
    )


def test_parse_mr_url_rejects_non_mr():
    with pytest.raises(ValueError):
        parse_mr_url("https://gitlab.com/group/proj/-/issues/5")


def test_build_request_encodes_path_and_sets_token():
    req = _build_request("gitlab.com", "group/proj", 5, token="t")
    assert req.full_url == (
        "https://gitlab.com/api/v4/projects/group%2Fproj/merge_requests/5/raw_diffs"
    )
    assert req.headers["Private-token"] == "t"


def test_build_request_without_token(monkeypatch):
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)
    req = _build_request("gitlab.com", "group/proj", 5)
    assert "Private-token" not in req.headers
