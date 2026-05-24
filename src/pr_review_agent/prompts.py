"""Prompt construction for the LLM review step."""
from __future__ import annotations

from .diff_parser import FileDiff

SYSTEM_PROMPT = (
    "You are a meticulous senior software engineer performing a code review on a "
    "pull/merge request diff. Focus on correctness bugs, security vulnerabilities, "
    "resource/concurrency issues, and clear maintainability problems. Do NOT nitpick "
    "style that a formatter would catch. Only comment on lines that were added "
    "(prefixed with '+').\n\n"
    "Respond with ONLY a JSON object of this exact shape:\n"
    '{"findings": [{"file": str, "line": int, "severity": str, "title": str, '
    '"detail": str, "suggestion": str}]}\n'
    "severity must be one of: critical, high, medium, low, info. "
    "line is the new-file line number shown in the prompt. "
    "If there are no issues, return {\"findings\": []}."
)


def build_user_prompt(file_diff: FileDiff) -> str:
    """Render a single file's diff with new-file line numbers for the model."""
    rendered: list[str] = []
    for ln in file_diff.lines:
        if ln.kind == "add":
            rendered.append(f"+{ln.new_lineno}: {ln.content}")
        elif ln.kind == "context":
            rendered.append(f" {ln.new_lineno}: {ln.content}")
        else:  # deletion — no new-file line number
            rendered.append(f"-    : {ln.content}")
    body = "\n".join(rendered)
    return (
        f"Review the changes to `{file_diff.path}`.\n"
        f"Lines prefixed with '+' are added, '-' removed, ' ' unchanged context.\n\n"
        f"{body}\n\n"
        f"Return JSON findings for problems in the added lines only."
    )
