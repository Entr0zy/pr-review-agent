import json

from pr_review_agent.diff_parser import parse_unified_diff
from pr_review_agent.llm.mock import MockLLMClient
from pr_review_agent.prompts import build_batch_prompt
from pr_review_agent.reviewer import PRReviewer

TWO_FILES = (
    "diff --git a/a.py b/a.py\n--- a/a.py\n+++ b/a.py\n@@ -0,0 +1,1 @@\n+a = 1\n"
    "diff --git a/b.py b/b.py\n--- a/b.py\n+++ b/b.py\n@@ -0,0 +1,1 @@\n+b = 2\n"
)


def test_build_batch_prompt_lists_all_files():
    prompt = build_batch_prompt(parse_unified_diff(TWO_FILES))
    assert "### FILE: a.py" in prompt
    assert "### FILE: b.py" in prompt


def test_batch_mode_one_call_when_budget_fits():
    canned = json.dumps(
        {"findings": [
            {"file": "a.py", "line": 1, "severity": "low", "title": "x"},
            {"file": "b.py", "line": 1, "severity": "high", "title": "y"},
        ]}
    )
    mock = MockLLMClient(response=canned)
    result = PRReviewer(mock, batch_char_budget=10_000).review_diff(TWO_FILES)
    assert len(mock.calls) == 1
    assert {f.file for f in result.findings} == {"a.py", "b.py"}
    assert result.has_blocking


def test_batch_mode_splits_when_budget_small():
    mock = MockLLMClient(responses=['{"findings": []}', '{"findings": []}'])
    PRReviewer(mock, batch_char_budget=1).review_diff(TWO_FILES)
    assert len(mock.calls) == 2
