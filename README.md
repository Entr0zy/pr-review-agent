# pr-review-agent

An AI agent that reviews pull/merge-request **diffs** and flags correctness bugs,
security issues, and risky changes — with findings mapped to exact file lines.

The design separates a small, dependency-free **review engine** from thin
**platform adapters**, so the same core can run as a Google Cloud agent, a Slack
app, or a GitHub App.

## Why it's built this way

```
diff text ──▶ diff_parser ──▶ prompts ──▶ LLMClient ──▶ findings (JSON) ──▶ ReviewResult
                                              ▲
                 Gemini | Heuristic(mock) | <your backend>
```

- `pr_review_agent.reviewer.PRReviewer` — the reusable engine (pure stdlib).
- `pr_review_agent.llm` — pluggable backends (`GeminiClient`, offline `HeuristicLLMClient`).
- `pr_review_agent.adapters` — per-platform glue (kept out of the core).

## Quickstart (no API key needed)

```bash
# Run the test suite
python -m pytest -q

# Review the bundled sample diff offline (no API key)
python -m pr_review_agent.cli --mock examples/sample.diff

# Review your working changes
git diff | python -m pr_review_agent.cli --mock

# Review a live GitHub PR by URL (uses GITHUB_TOKEN if set)
python -m pr_review_agent.cli --github-pr https://github.com/OWNER/REPO/pull/N --mock
```

See [docs/architecture.md](docs/architecture.md) for the design and
[docs/demo-script.md](docs/demo-script.md) for the demo walkthrough.

Example output:

```
3 finding(s): 1 critical, 1 high, 1 low
  [CRITICAL] app.py:1 - Possible hardcoded secret
      Move credentials to environment variables or a secret manager.
  [HIGH] app.py:2 - Use of eval()
      eval() can execute arbitrary code; use a safe parser instead.
```

## Real reviews with Gemini

```bash
pip install "pr-review-agent[gemini]"
export GEMINI_API_KEY=...
git diff main...HEAD | python -m pr_review_agent.cli
```

## Google Cloud Agent Builder + GitLab MCP

The GitLab hackathon track has a deployable ADK agent in
`agents/gitlab_reviewer/agent.py`. It runs on Gemini 3 and connects to GitLab's
official HTTP MCP endpoint, so it can inspect merge requests and, after explicit
approval, post review findings back to GitLab.

```bash
pip install -e ".[cloud]"
export GOOGLE_API_KEY=...
adk web agents
```

The default model is `gemini-3-pro-preview` and the default MCP endpoint is
`https://gitlab.com/api/v4/mcp`. GitLab authentication occurs through its MCP
OAuth flow; a hosted runtime can supply its resulting bearer token through
`GITLAB_MCP_AUTH_TOKEN` from secret configuration.

See [docs/google-cloud-gitlab.md](docs/google-cloud-gitlab.md) for configuration,
cloud deployment, and demo steps.

## Use as a GitHub Action

```yaml
# .github/workflows/review.yml
name: PR Review
on: pull_request
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Entr0zy/pr-review-agent@main
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          gemini-api-key: ${{ secrets.GEMINI_API_KEY }}  # omit to run the offline heuristic
          fail-on: high
```

## CLI options

| Flag | Purpose |
|---|---|
| `--github-pr URL` / `--gitlab-mr URL` | review a live PR/MR (auto-fetches the diff) |
| `--mock` | offline heuristic reviewer (no API key) |
| `--format text\|json\|markdown` | output format |
| `--fail-on critical\|high\|medium\|low\|info\|none` | exit-code threshold |

## Roadmap (adapters)

| Adapter | Surface | Status |
|---|---|---|
| `agents/gitlab_reviewer`, `adapters/gitlab_mcp.py` | Google Cloud Agent Builder + Gemini 3 + GitLab MCP | implemented; deploy/auth required |
| `adapters/slack_app.py` | Slack app (MCP integration) | stub |
| `adapters/github_app.py` | GitHub App / Marketplace (PR webhooks) | core implemented (signature verify + payload parse) |
| `sources/github.py`, `sources/gitlab.py` | fetch PR/MR diffs | implemented |

## License

MIT — see [LICENSE](LICENSE).
