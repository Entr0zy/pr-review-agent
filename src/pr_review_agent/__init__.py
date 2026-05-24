"""pr-review-agent: an AI agent that reviews PR/MR diffs for bugs and risks."""
from .diff_parser import DiffLine, FileDiff, parse_unified_diff
from .models import Finding, ReviewResult, Severity
from .reviewer import PRReviewer

__all__ = [
    "Finding",
    "ReviewResult",
    "Severity",
    "PRReviewer",
    "parse_unified_diff",
    "FileDiff",
    "DiffLine",
]
__version__ = "0.1.0"
