"""Command-line entry point.

Examples:
    # offline demo, no API key needed:
    git diff | python -m pr_review_agent.cli --mock

    # real review with Gemini (needs GEMINI_API_KEY and the [gemini] extra):
    git diff main...HEAD | python -m pr_review_agent.cli
"""
from __future__ import annotations

import argparse
import sys

from .reviewer import PRReviewer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review a unified diff for bugs and risks.")
    parser.add_argument("diff", nargs="?", help="Path to a diff file. Reads stdin if omitted.")
    parser.add_argument("--mock", action="store_true",
                        help="Use the offline heuristic reviewer (no API key).")
    parser.add_argument("--model", default="gemini-2.5-pro", help="Gemini model id.")
    args = parser.parse_args(argv)

    diff_text = open(args.diff, encoding="utf-8").read() if args.diff else sys.stdin.read()

    if args.mock:
        from .llm.mock import HeuristicLLMClient
        llm = HeuristicLLMClient()
    else:
        from .llm.gemini import GeminiClient
        llm = GeminiClient(model=args.model)

    result = PRReviewer(llm).review_diff(diff_text)

    print(result.summary)
    for f in result.findings:
        loc = f"{f.file}:{f.line}" if f.line else f.file
        print(f"  [{f.severity.value.upper()}] {loc} - {f.title}")
        if f.detail:
            print(f"      {f.detail}")
        if f.suggestion:
            print(f"      -> {f.suggestion}")

    return 1 if result.has_blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
