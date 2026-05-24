import json

from pr_review_agent.llm.mock import HeuristicLLMClient, MockLLMClient
from pr_review_agent.models import Severity
from pr_review_agent.reviewer import PRReviewer

DIFF = """diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -0,0 +1,3 @@
+password = "hunter2"
+result = eval(user_input)
+print(result)
"""


def test_parses_canned_findings():
    canned = json.dumps(
        {"findings": [{"file": "app.py", "line": 2, "severity": "high",
                       "title": "eval", "detail": "bad"}]}
    )
    result = PRReviewer(MockLLMClient(response=canned)).review_diff(DIFF)
    assert len(result.findings) == 1
    assert result.findings[0].severity is Severity.HIGH
    assert result.findings[0].line == 2
    assert result.has_blocking


def test_lenient_json_in_code_fence():
    canned = "```json\n" + json.dumps(
        {"findings": [{"severity": "low", "title": "print", "line": 3}]}
    ) + "\n```"
    result = PRReviewer(MockLLMClient(response=canned)).review_diff(DIFF)
    assert len(result.findings) == 1
    assert result.findings[0].file == "app.py"  # filled in from diff path
    assert not result.has_blocking


def test_invalid_severity_falls_back_to_info():
    canned = json.dumps({"findings": [{"title": "x", "severity": "spicy"}]})
    result = PRReviewer(MockLLMClient(response=canned)).review_diff(DIFF)
    assert result.findings[0].severity is Severity.INFO


def test_no_findings_summary():
    result = PRReviewer(MockLLMClient(response='{"findings": []}')).review_diff(DIFF)
    assert result.summary == "No issues found."
    assert not result.has_blocking


def test_heuristic_client_end_to_end():
    result = PRReviewer(HeuristicLLMClient()).review_diff(DIFF)
    titles = {f.title.lower() for f in result.findings}
    assert any("secret" in t for t in titles)
    assert any("eval" in t for t in titles)
    assert result.has_blocking
    assert all(f.file == "app.py" for f in result.findings)


def test_skips_files_with_no_additions():
    diff = (
        "diff --git a/x.py b/x.py\n"
        "--- a/x.py\n"
        "+++ b/x.py\n"
        "@@ -1,2 +1,1 @@\n"
        " keep\n"
        "-removed\n"
    )
    mock = MockLLMClient()
    result = PRReviewer(mock).review_diff(diff)
    assert mock.calls == []
    assert result.findings == []
