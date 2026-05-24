"""Core data models for review findings (platform-agnostic)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

    @property
    def is_blocking(self) -> bool:
        return self in (Severity.CRITICAL, Severity.HIGH)


@dataclass
class Finding:
    """A single issue raised by the reviewer about a changed line."""

    file: str
    severity: Severity
    title: str
    detail: str = ""
    line: int | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "severity": self.severity.value,
            "title": self.title,
            "detail": self.detail,
            "suggestion": self.suggestion,
        }


@dataclass
class ReviewResult:
    """The outcome of reviewing a whole diff."""

    findings: list[Finding] = field(default_factory=list)
    summary: str = ""

    @property
    def has_blocking(self) -> bool:
        return any(f.severity.is_blocking for f in self.findings)

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "has_blocking": self.has_blocking,
            "findings": [f.to_dict() for f in self.findings],
        }
