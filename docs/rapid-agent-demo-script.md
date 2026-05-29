# Rapid Agent — 3-minute demo video script

Target: Google Cloud Rapid Agent Hackathon submission (deadline Jun 11).
The judges scoring rubric weights three things: **Gemini 3 usage**, **Agent
Builder / ADK integration**, and **partner MCP integration** (GitLab MCP).
This script hits all three in three minutes.

## Setup before you hit record

1. Close every browser tab except: **one GitLab tab on your test MR #1**
   ([`personal-project!1`](https://gitlab.com/personal-group5841022/personal-project/-/merge_requests/1))
   and **one tab on the GitHub repo** (`Entr0zy/pr-review-agent`).
2. Open a clean terminal in `C:\Users\TEZ NEW\Documents\pr-review-agent`.
3. Source the env once and leave it open: `set -a && . ./.env && set +a`.
4. Recording tool: **Win+G → Capture → Start recording**. Aim for **1080p**.
5. Upload as **Unlisted** on YouTube when done; paste the link into Devpost.

## Shot list (read this top-to-bottom while recording)

### 0:00 – 0:25 — Problem & hook
**On screen:** the GitLab MR diff (`payment.py`), zoomed so the planted bugs
(`STRIPE_KEY = "..."`, the `%s` SQL formatting, and `eval(...)`) are visible.

**Say:**
> "Every team has the same bottleneck: code review. Senior engineers spend
> hours a week on diffs and still miss real security bugs because attention
> runs out. **MergeGuard** is an autonomous reviewer built on Google Cloud
> Agent Builder and Gemini 3. It catches leaked secrets, injection bugs, and
> unsafe code on every merge request — automatically."

### 0:25 – 1:30 — Live demo
**On screen:** terminal, full-screen. Type the command (don't paste — judges
like to see the keystrokes).

**Run:**
```bash
python -m pr_review_agent.cli \
  --gitlab-mr https://gitlab.com/personal-group5841022/personal-project/-/merge_requests/1 \
  --model gemini-3.1-pro-preview \
  --format markdown
```

**Say (while it runs, ~5–10s):**
> "The agent fetches the merge request diff from GitLab, sends it through
> Gemini 3 Pro on Vertex AI with a structured-output JSON schema, and gets
> back line-mapped findings with concrete fix suggestions."

**When findings print, point at each:**
> "Two critical findings on this PR: a SQL injection at line 11, and a remote
> code execution via `eval` at line 13. Each one has the file, the exact line
> number, the impact, and a fix the developer can paste in."

**Then run the post-back command:**
```bash
python -m pr_review_agent.cli \
  --gitlab-mr https://gitlab.com/personal-group5841022/personal-project/-/merge_requests/1 \
  --model gemini-3.1-pro-preview --post
```

**Switch to the GitLab browser tab, refresh, scroll to the new note.**

**Say:**
> "And here's the review posted right back to the merge request, ready for the
> developer to act on."

### 1:30 – 2:15 — Under the hood (architecture + ADK + MCP)
**Switch to the GitHub repo,** open `docs/architecture.md`. The Mermaid
diagram renders inline.

**Say:**
> "Three layers. Sources fetch the diff via REST. A platform-agnostic engine
> prompts Gemini 3 with a strict JSON schema and parses findings mapped to
> file lines. Per-platform adapters post results back."

**Open `agents/gitlab_reviewer/agent.py` on GitHub** (one screen of code).

**Say:**
> "The Agent Builder entrypoint lives here — a Google ADK `root_agent` built
> on Gemini 3.1 Pro and wired to GitLab's official MCP server. The same agent
> runs locally in `adk web agents` and deploys to Vertex Agent Engine
> unchanged. The MCP integration means the agent can ask GitLab for project
> metadata, fetch any merge request, and post review notes — all through the
> partner MCP, with explicit human approval gates before any write."

**(Optional) flick to a terminal and show:**
```bash
adk web agents
```
…showing the local Agent Builder UI listing **mergeguard_gitlab_reviewer**.
A 2-second flash is enough.

### 2:15 – 2:45 — Impact
**Back to the live review output in the terminal.**

**Say:**
> "Why this matters. Three categories of real-world bugs caught before merge:
> leaked credentials, injection vulnerabilities, and unsafe `eval`. It's
> open-source under MIT, runs as a CLI, a GitHub Action, a Slack bot, or a
> deployed Google Cloud agent. CI is green, 49 tests, public repo."

### 2:45 – 3:00 — Close
**On screen:** the GitHub repo page (`github.com/Entr0zy/pr-review-agent`).

**Say:**
> "MergeGuard. Autonomous code review on Google Cloud Agent Builder, powered
> by Gemini 3. Repo and deploy guide linked below. Thanks for watching."

## Hard-won tips
- **Don't read off the script word-for-word** — it sounds scripted. Speak from
  memory; this is a guide, not a teleprompter.
- **One take is fine if you flub a single word.** Stop, breathe, restart that
  sentence — most editors keep the good half.
- **Mute your mic when typing** — typing noise is the #1 polish-killer.
- **End on the repo URL on screen for 2 seconds** so it sticks in the judge's
  head.
- If `adk web agents` hangs or errors during the take, **skip that shot** —
  the architecture and the live review carry the demo on their own.
