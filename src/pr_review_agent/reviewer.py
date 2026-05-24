"""The platform-agnostic review engine.

Given diff text and any :class:`LLMClient`, produce a :class:`ReviewResult`.
This is the reusable core shared across every hackathon adapter (Google Cloud
Agent Builder, Slack, GitHub App, ...).
"""
from __future__ import annotations

import json
import re
from collections import Counter

from .diff_parser import FileDiff, parse_unified_diff
from .llm.base import LLMClient
from .models import Finding, ReviewResult, Severity
from .prompts import SYSTEM_PROMPT, build_batch_prompt, build_user_prompt


class PRReviewer:
    """Review a diff with an LLM backend.

    Args:
        llm: any object implementing ``complete(system, user) -> str``.
        max_files: cap on number of changed files reviewed.
        batch_char_budget: if set, files are grouped into batched prompts up to
            this many characters per call (fewer API calls). If ``None`` (default)
            each file is reviewed in its own call for the tightest line mapping.
    """

    def __init__(self, llm: LLMClient, max_files: int = 50,
                 batch_char_budget: int | None = None):
        self.llm = llm
        self.max_files = max_files
        self.batch_char_budget = batch_char_budget

    def review_diff(self, diff_text: str) -> ReviewResult:
        files = [fd for fd in parse_unified_diff(diff_text)[: self.max_files]
                 if fd.added_lines]
        result = ReviewResult()
        if not files:
            result.summary = self._summarize(result)
            return result

        if self.batch_char_budget:
            for chunk in self._chunk(files, self.batch_char_budget):
                raw = self.llm.complete(SYSTEM_PROMPT, build_batch_prompt(chunk))
                result.findings.extend(self._parse_findings(chunk[0].path, raw))
        else:
            for fd in files:
                raw = self.llm.complete(SYSTEM_PROMPT, build_user_prompt(fd))
                result.findings.extend(self._parse_findings(fd.path, raw))

        result.summary = self._summarize(result)
        return result

    @staticmethod
    def _chunk(files: list[FileDiff], budget: int) -> list[list[FileDiff]]:
        chunks: list[list[FileDiff]] = []
        current: list[FileDiff] = []
        size = 0
        for fd in files:
            approx = sum(len(ln.content) + 8 for ln in fd.lines) + len(fd.path)
            if current and size + approx > budget:
                chunks.append(current)
                current, size = [], 0
            current.append(fd)
            size += approx
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _parse_findings(default_path: str, raw: str) -> list[Finding]:
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
                    file=item.get("file") or default_path,
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
