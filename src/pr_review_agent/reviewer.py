"""The platform-agnostic review engine.

Given diff text and any :class:`LLMClient`, produce a :class:`ReviewResult`.
This is the reusable core shared across every hackathon adapter (Google Cloud
Agent Builder, Slack, GitHub App, ...).
"""
from __future__ import annotations

import json
import re
from collections import Counter

from .diff_parser import parse_unified_diff
from .llm.base import LLMClient
from .models import Finding, ReviewResult, Severity
from .prompts import SYSTEM_PROMPT, build_user_prompt


class PRReviewer:
    def __init__(self, llm: LLMClient, max_files: int = 50):
        self.llm = llm
        self.max_files = max_files

    def review_diff(self, diff_text: str) -> ReviewResult:
        files = parse_unified_diff(diff_text)[: self.max_files]
        result = ReviewResult()
        for fd in files:
            if not fd.added_lines:
                continue
            raw = self.llm.complete(SYSTEM_PROMPT, build_user_prompt(fd))
            result.findings.extend(self._parse_findings(fd.path, raw))
        result.summary = self._summarize(result)
        return result

    @staticmethod
    def _parse_findings(path: str, raw: str) -> list[Finding]:
        data = _loads_lenient(raw)
        findings: list[Finding] = []
        for item in data.get("findings", []):
            if not isinstance(item, dict):
                continue
            try:
                severity = Severity(str(item.get("severity", "info")).lower())
            except ValueError:
                severity = Severity.INFO
            line = item.get("line")
            findings.append(
                Finding(
                    file=item.get("file") or path,
                    severity=severity,
                    title=str(item.get("title", "")).strip(),
                    detail=str(item.get("detail", "")).strip(),
                    line=int(line) if isinstance(line, (int, str)) and str(line).isdigit() else None,
                    suggestion=(item.get("suggestion") or None),
                )
            )
        return findings

    @staticmethod
    def _summarize(result: ReviewResult) -> str:
        if not result.findings:
            return "No issues found."
        counts = Counter(f.severity.value for f in result.findings)
        order = ["critical", "high", "medium", "low", "info"]
        parts = [f"{counts[s]} {s}" for s in order if counts[s]]
        return f"{len(result.findings)} finding(s): " + ", ".join(parts)


def _loads_lenient(raw: str) -> dict:
    """Parse JSON that may be wrapped in markdown code fences or surrounded by prose."""
    if not raw:
        return {}
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return {}
        return {}
