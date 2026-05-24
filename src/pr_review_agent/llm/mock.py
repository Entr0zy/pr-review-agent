"""Offline LLM clients for tests and credential-free demos."""
from __future__ import annotations

import json
import re


class MockLLMClient:
    """Returns canned responses. Useful for deterministic unit tests."""

    def __init__(self, response: str | None = None, responses: list[str] | None = None):
        self._response = response
        self._responses = list(responses) if responses else None
        self.calls: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        if self._responses is not None:
            return self._responses.pop(0) if self._responses else '{"findings": []}'
        if self._response is not None:
            return self._response
        return '{"findings": []}'


# Simple pattern-based "reviewer" so `--mock` produces real output with no API key.
_PATTERNS: list[tuple[re.Pattern, str, str, str]] = [
    (re.compile(r"(?i)(password|secret|api[_-]?key|token)\s*=\s*['\"]"),
     "critical", "Possible hardcoded secret",
     "Move credentials to environment variables or a secret manager."),
    (re.compile(r"\beval\s*\("),
     "high", "Use of eval()",
     "eval() can execute arbitrary code; use a safe parser instead."),
    (re.compile(r"\bexcept\s*:\s*$"),
     "medium", "Bare except clause",
     "Catch specific exceptions so real errors are not swallowed."),
    (re.compile(r"\bprint\s*\("),
     "low", "Debug print left in code",
     "Remove or switch to a logger."),
    (re.compile(r"\b(TODO|FIXME)\b"),
     "info", "Unresolved TODO/FIXME",
     "Track this as a follow-up issue."),
]


class HeuristicLLMClient:
    """A keyword-driven stand-in that flags obvious issues in added lines.

    Not a real model — it just lets the CLI demo run end-to-end offline.
    """

    def complete(self, system: str, user: str) -> str:
        findings = []
        for match in re.finditer(r"^\+(\d+): (.*)$", user, re.MULTILINE):
            lineno, text = int(match.group(1)), match.group(2)
            for pattern, severity, title, detail in _PATTERNS:
                if pattern.search(text):
                    findings.append(
                        {"line": lineno, "severity": severity, "title": title, "detail": detail}
                    )
        return json.dumps({"findings": findings})
