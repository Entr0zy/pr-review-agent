"""GitLab MCP adapter — TARGET: Google Cloud Rapid Agent Hackathon (deadline ~Jun 11).

Plan:
  1. Run the agent on Google Cloud Agent Builder with a Gemini 3 model.
  2. Connect the GitLab MCP server (a listed partner) as a tool source so the
     agent can list merge requests, fetch a diff, and post review comments.
  3. Pipe the fetched diff through `PRReviewer.review_diff` and map findings to
     MR discussion threads via the MCP `create_merge_request_note` tool.

This is a stub: fill in once the Google Cloud + GitLab MCP credentials exist.
"""
from __future__ import annotations


def review_merge_request(project_id: str, mr_iid: int) -> None:
    raise NotImplementedError(
        "Wire up the GitLab MCP server + Gemini client, then call "
        "PRReviewer(GeminiClient()).review_diff(<fetched diff>)."
    )
