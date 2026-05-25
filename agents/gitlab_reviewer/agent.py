"""ADK discovery entrypoint for the GitLab partner-track agent."""

from pr_review_agent.adapters.gitlab_mcp import build_agent

root_agent = build_agent()
