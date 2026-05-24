"""Minimal unified-diff parser.

Turns `git diff` / merge-request patch text into per-file structures that know
the *new-file* line number of every added/context line, so findings can be
mapped back to concrete lines. Pure stdlib; no external dependencies.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Captures the starting new-file line number from a hunk header:
#   @@ -12,7 +15,9 @@  ->  group(1) == "15"
_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


@dataclass
class DiffLine:
    content: str
    kind: str  # "add" | "del" | "context"
    new_lineno: int | None = None


@dataclass
class FileDiff:
    path: str
    lines: list[DiffLine] = field(default_factory=list)

    @property
    def added_lines(self) -> list[DiffLine]:
        return [ln for ln in self.lines if ln.kind == "add"]


def parse_unified_diff(diff_text: str) -> list[FileDiff]:
    """Parse unified diff text into a list of :class:`FileDiff`."""
    files: list[FileDiff] = []
    current: FileDiff | None = None
    new_lineno = 0

    for raw in diff_text.splitlines():
        if raw.startswith("diff --git") or raw.startswith("index "):
            continue
        if raw.startswith("--- "):
            continue
        if raw.startswith("+++ "):
            path = raw[4:].strip()
            if path.startswith("b/"):
                path = path[2:]
            current = FileDiff(path=path)
            files.append(current)
            continue

        hunk = _HUNK_RE.match(raw)
        if hunk:
            new_lineno = int(hunk.group(1))
            continue

        if current is None or raw.startswith("\\"):
            # e.g. "\ No newline at end of file"
            continue

        if raw.startswith("+"):
            current.lines.append(DiffLine(raw[1:], "add", new_lineno))
            new_lineno += 1
        elif raw.startswith("-"):
            current.lines.append(DiffLine(raw[1:], "del", None))
        else:
            content = raw[1:] if raw.startswith(" ") else raw
            current.lines.append(DiffLine(content, "context", new_lineno))
            new_lineno += 1

    return files
