"""Command-line entry point.

Examples:
    # offline demo, no API key needed:
    python -m pr_review_agent.cli --mock examples/sample.diff

    # review a live GitHub PR or GitLab MR (uses GITHUB_TOKEN / GITLAB_TOKEN if set):
    python -m pr_review_agent.cli --github-pr https://github.com/owner/repo/pull/1 --mock
    python -m pr_review_agent.cli --gitlab-mr https://gitlab.com/grp/proj/-/merge_requests/1 --mock

    # real review with Gemini, as markdown:
    git diff main...HEAD | python -m pr_review_agent.cli --format markdown
"""
from __future__ import annotations

import argparse
import sys

from .agent import review_url
from .models import ReviewResult
from .reviewer import PRReviewer

_SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]


def _make_llm(args: argparse.Namespace):
    if args.mock:
        from .llm.mock import HeuristicLLMClient
        return HeuristicLLMClient()
    from .llm.gemini import GeminiClient
    return GeminiClient(model=args.model)


def _exit_code(result: ReviewResult, fail_on: str) -> int:
    if fail_on == "none" or not result.findings:
        return 0
    threshold = _SEVERITY_ORDER.index(fail_on)
    worst = min(_SEVERITY_ORDER.index(f.severity.value) for f in result.findings)
    return 1 if worst <= threshold else 0


def _render(result: ReviewResult, fmt: str) -> None:
    if fmt == "json":
        from .output import to_json
        print(to_json(result))
        return
    if fmt == "markdown":
        from .output import to_markdown
        print(to_markdown(result))
        return
    print(result.summary)
    for f in result.findings:
        loc = f"{f.file}:{f.line}" if f.line else f.file
        print(f"  [{f.severity.value.upper()}] {loc} - {f.title}")
        if f.detail:
            print(f"      {f.detail}")
        if f.suggestion:
            print(f"      -> {f.suggestion}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review a unified diff for bugs and risks.")
    parser.add_argument("diff", nargs="?", help="Path to a diff file. Reads stdin if omitted.")
    parser.add_argument("--github-pr", metavar="URL", help="Review a GitHub PR by URL.")
    parser.add_argument("--gitlab-mr", metavar="URL", help="Review a GitLab MR by URL.")
    parser.add_argument("--mock", action="store_true",
                        help="Use the offline heuristic reviewer (no API key).")
    parser.add_argument("--model", default="gemini-2.5-pro", help="Gemini model id.")
    parser.add_argument("--format", dest="fmt", choices=["text", "json", "markdown"],
                        default="text", help="Output format (default: text).")
    parser.add_argument("--fail-on", dest="fail_on",
                        choices=[*_SEVERITY_ORDER, "none"], default="high",
                        help="Exit non-zero if a finding at/above this severity exists.")
    args = parser.parse_args(argv)

    llm = _make_llm(args)
    url = args.github_pr or args.gitlab_mr
    if url:
        result = review_url(url, llm)
    else:
        diff_text = open(args.diff, encoding="utf-8").read() if args.diff else sys.stdin.read()
        result = PRReviewer(llm).review_diff(diff_text)

    _render(result, args.fmt)
    return _exit_code(result, args.fail_on)


if __name__ == "__main__":
    raise SystemExit(main())
