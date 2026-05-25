# Google Cloud Agent Builder and GitLab MCP

This repository includes a submission-ready agent entrypoint for the GitLab
track of the Google Cloud Rapid Agent Hackathon:

- `agents/gitlab_reviewer/agent.py` exports the ADK `root_agent`.
- `src/pr_review_agent/adapters/gitlab_mcp.py` configures the agent.
- Gemini 3 performs the review reasoning.
- GitLab's official MCP server supplies merge request reads and approved writes.

## Why this meets the track requirement

The agent is not a chat-only assistant. It follows a controlled workflow:

1. Retrieve a GitLab merge request and its changed code using GitLab MCP tools.
2. Analyze the change for correctness, security, regression, and test risks.
3. Produce file-and-line review findings ranked by severity.
4. Ask for explicit human approval before creating GitLab comments.
5. Post the approved findings through GitLab MCP tools.

The write confirmation is intentional: GitLab's MCP documentation warns clients
to guard against prompt injection in untrusted repository content.

## Local run

Install the cloud adapter:

```bash
python -m pip install -e ".[cloud]"
```

Set Gemini authentication for the ADK environment:

```bash
export GOOGLE_API_KEY="..."
```

Start ADK's development UI from the repository root:

```bash
adk web agents
```

Select `gitlab_reviewer`. When the agent first connects to
`https://gitlab.com/api/v4/mcp`, complete GitLab's OAuth authorization flow.

## Configuration

The defaults are aligned with the hackathon partner track:

| Environment variable | Default | Purpose |
|---|---|---|
| `PR_REVIEW_MODEL` | `gemini-3-pro-preview` | Gemini 3 model used by ADK |
| `GITLAB_MCP_URL` | `https://gitlab.com/api/v4/mcp` | GitLab MCP HTTP endpoint |
| `GITLAB_MCP_TOOL_PREFIX` | `gitlab_` | Avoid tool-name collisions |
| `GITLAB_MCP_AUTH_TOKEN` | unset | OAuth bearer token supplied as a deployed secret |

The official MCP server handles user authorization through OAuth. For a hosted
runtime, inject the resulting bearer token from secret configuration; never
commit it to the repository or put it in the demo video.

## Cloud deployment

Deploy the ADK application from `agents/gitlab_reviewer` to Google Cloud Agent
Builder / Agent Engine Runtime using the Google Cloud project selected for the
submission. Set `PR_REVIEW_MODEL=gemini-3-pro-preview` in the deployed runtime
and supply the demo account's authorized GitLab MCP token as the
`GITLAB_MCP_AUTH_TOKEN` runtime secret.

The hosted agent URL is required in the Devpost submission. The public
repository, MIT license, and approximately three-minute demo video cover the
remaining technical artifacts.

## Demo prompt

```text
Review the merge request at <GitLab MR URL>. Find blocking correctness and
security risks. Show the review first; do not post anything until I approve.
```

After examining the proposed review, approve posting and show the resulting
GitLab merge request notes in the video.

## References

- Google Cloud Rapid Agent Hackathon: https://rapid-agent.devpost.com/
- Vertex AI Agent Builder: https://cloud.google.com/products/agent-builder
- Google ADK MCP tools: https://google.github.io/adk-docs/tools-custom/mcp-tools/
- GitLab MCP server: https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/
