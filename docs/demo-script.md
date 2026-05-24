# 3-minute demo / video script

Most Devpost agent hackathons score a **~3-minute demo video**. This is a shot
list + narration you can record once the cloud adapter is wired.

## Setup (before recording)
- Terminal with the repo checked out, tests passing.
- A browser tab on a real GitHub PR (or use `examples/sample.diff`).
- (For the live agent) the deployed Google Cloud Agent Builder URL.

## Shot list

**0:00–0:25 — Problem.**
"Code review is the bottleneck on every team. Reviewers miss security bugs in
large diffs. `pr-review-agent` is an autonomous agent that reviews a pull request
and reports line-level findings in seconds."

**0:25–0:55 — Architecture (show `docs/architecture.md` diagram).**
"A dependency-free engine parses the diff, prompts Gemini 3 with a strict JSON
schema, and returns findings. Sources and platform adapters are pluggable."

**0:55–1:50 — Live demo.**
- Run the offline path first (no secrets on screen):
  ```bash
  python -m pr_review_agent.cli --mock examples/sample.diff
  ```
  Point out it flags the hardcoded Stripe key, the SQL-injection string, and `eval()`.
- Then the real agent (Google Cloud + Gemini + GitLab MCP): trigger a review on a
  live merge request; show findings posted back as MR comments.

**1:50–2:30 — Under the hood.**
"Findings are schema-constrained JSON mapped to exact file lines. The engine
batches files to cut API calls. The same core runs as a Slack app and a GitHub
App." (show `reviewer.py` + the `adapters/` folder briefly.)

**2:30–3:00 — Impact + close.**
"It catches real classes of bugs — secrets, injection, unsafe eval — before they
merge, on any forge. Open source, MIT licensed." Show the repo URL.

## Exact commands used in the demo
```bash
# tests
python -m pytest -q

# offline review of the bundled sample
python -m pr_review_agent.cli --mock examples/sample.diff

# live GitHub PR (uses GITHUB_TOKEN if set)
python -m pr_review_agent.cli --github-pr https://github.com/OWNER/REPO/pull/N --mock
```
