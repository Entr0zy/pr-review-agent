"""Prompt construction and the structured-output schema for the LLM review step."""
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
    "Always include the `file` field. "
    "If there are no issues, return {\"findings\": []}."
)

# Structured-output schema passed to Gemini (response_schema) so the model is
# constrained to return exactly this shape.
RESPONSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "severity": {
                        "type": "string",
                        "enum": ["critical", "high", "medium", "low", "info"],
                    },
                    "title": {"type": "string"},
                    "detail": {"type": "string"},
                    "suggestion": {"type": "string"},
                },
                "required": ["file", "severity", "title"],
            },
        }
    },
    "required": ["findings"],
}


def _render_lines(file_diff: FileDiff) -> str:
    rendered: list[str] = []
    for ln in file_diff.lines:
        if ln.kind == "add":
            rendered.append(f"+{ln.new_lineno}: {ln.content}")
        elif ln.kind == "context":
            rendered.append(f" {ln.new_lineno}: {ln.content}")
        else:  # deletion — no new-file line number
            rendered.append(f"-    : {ln.content}")
    return "\n".join(rendered)


def build_user_prompt(file_diff: FileDiff) -> str:
    """Render a single file's diff with new-file line numbers for the model."""
    return (
        f"Review the changes to `{file_diff.path}`.\n"
        f"Lines prefixed with '+' are added, '-' removed, ' ' unchanged context.\n\n"
        f"{_render_lines(file_diff)}\n\n"
        f"Return JSON findings for problems in the added lines only."
    )


def build_batch_prompt(files: list[FileDiff]) -> str:
    """Render several files in one prompt to reduce LLM round-trips.

    Each finding MUST carry the `file` it refers to, since multiple files share
    the response.
    """
    sections = [f"### FILE: {fd.path}\n{_render_lines(fd)}" for fd in files]
    return (
        "Review the following changed files. Each finding MUST include the exact "
        "`file` path it refers to. Lines prefixed with '+' are added.\n\n"
        + "\n\n".join(sections)
        + "\n\nReturn JSON findings for problems in the added lines only."
    )
