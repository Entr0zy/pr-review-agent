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
export GEMINI_API_KEY=...        # set the model id to Gemini 3 in llm/gemini.py
git diff main...HEAD | python -m pr_review_agent.cli
```

## Roadmap (adapters)

| Adapter | Surface | Status |
|---|---|---|
| `adapters/gitlab_mcp.py` | Google Cloud Agent Builder + Gemini 3 + GitLab MCP | stub |
| `adapters/slack_app.py` | Slack app (MCP integration) | stub |
| `adapters/github_app.py` | GitHub App / Marketplace (PR webhooks) | stub |

## License

MIT — see [LICENSE](LICENSE).
