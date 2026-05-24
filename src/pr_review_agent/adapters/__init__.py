"""Per-platform adapters that wrap the shared review engine.

Each hackathon target mandates a different orchestration layer; these modules
keep that platform-specific glue isolated from the reusable core in
``pr_review_agent.reviewer``.
"""
