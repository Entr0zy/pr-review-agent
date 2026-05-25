from pr_review_agent.agent import review_url
from pr_review_agent.llm.mock import HeuristicLLMClient, MockLLMClient

DIFF = (
    'diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n'
    '@@ -0,0 +1,1 @@\n+password = "x"\n'
)


def test_review_url_with_injected_fetcher():
    result = review_url(
        "https://github.com/o/r/pull/1",
        HeuristicLLMClient(),
        fetcher=lambda url, token: DIFF,
    )
    assert result.has_blocking
    assert result.findings[0].file == "a.py"


def test_auto_fetch_routes_to_gitlab(monkeypatch):
    import pr_review_agent.sources.github as gh
    import pr_review_agent.sources.gitlab as gl

    used: dict[str, str] = {}

    def fake_gl(url, token=None):
        used["gitlab"] = url
        return DIFF

    def fake_gh(url, token=None):
        used["github"] = url
        return DIFF

    monkeypatch.setattr(gl, "fetch_mr_diff_from_url", fake_gl)
    monkeypatch.setattr(gh, "fetch_pr_diff_from_url", fake_gh)

    review_url("https://gitlab.com/g/p/-/merge_requests/3", MockLLMClient())
    assert "gitlab" in used and "github" not in used
