# Slack Agent Builder — 3-minute demo video script

Target: Slack Agent Builder Challenge submission (deadline Jul 13).
The judges weight: **a real working Slack app**, **MCP integration** (we use
the GitHub/GitLab MCP via our review engine), and a clean **agent
interaction** in Slack. This script hits all three in three minutes.

## Setup before you hit record

1. Tabs open: **Slack** (with #new-channel selected) and **GitLab MR #1**
   ([`personal-project!1`](https://gitlab.com/personal-group5841022/personal-project/-/merge_requests/1)).
2. Terminal in `C:\Users\TEZ NEW\Documents\pr-review-agent`, the Slack app
   already running:
   ```bash
   set -a && . ./.env && set +a
   PYTHONPATH=src python -m pr_review_agent.adapters.slack_app
   ```
   Wait until the log shows `Bolt app is running!`.
3. Recording tool: **Win+G → Capture → Start recording**. Aim for **1080p**.
4. Upload as **Unlisted** on YouTube; paste the link into Devpost.

## Shot list

### 0:00 – 0:25 — Problem & hook
**On screen:** the GitLab MR diff (`payment.py`), zoomed so the bugs are visible.

**Say:**
> "Code review is the bottleneck on every team. Senior engineers spend hours a
> week on diffs and still miss real security bugs. I built **MergeGuard for
> Slack**: a Slack agent that reviews any pull request or merge request right
> from a channel — powered by Gemini and the GitHub/GitLab MCP."

### 0:25 – 1:40 — Live demo
**Switch to Slack, #new-channel.** Type the slash command slowly so the auto-
complete shows it's registered:

```
/review https://gitlab.com/personal-group5841022/personal-project/-/merge_requests/1
```

**Press Enter. The bot replies within a few seconds with a Block Kit message.**

**Say (while it loads, ~5–10s):**
> "The slash command triggers the Slack app over Socket Mode. The app fetches
> the diff via the GitLab REST source — the same code that backs our Agent
> Builder track's MCP integration — sends it through Gemini with a structured
> JSON schema, and posts findings right back here in Slack."

**When findings appear, point at each one:**
> "Three findings on this merge request. A hardcoded Stripe key flagged HIGH —
> exposed credentials. A SQL injection vulnerability flagged CRITICAL — the
> `%s` formatting on user input. And a remote code execution via `eval`,
> CRITICAL again. Each finding shows file, line, severity, and a short
> explanation."

### 1:40 – 2:20 — Under the hood
**Switch to the GitHub repo (`Entr0zy/pr-review-agent`), open
`docs/architecture.md`.** The Mermaid diagram renders inline.

**Say:**
> "Architecture: a platform-agnostic review engine in pure Python — diff parser,
> structured-output Gemini prompt, line-mapped findings. Then thin per-platform
> adapters. The Slack adapter is just a Slack Bolt app: a `/review` command
> handler that hands the URL to the agent and renders the findings as Block
> Kit blocks. The same engine runs as a CLI, a GitHub Action, and a Google
> Cloud Agent Builder agent connected to GitLab's official MCP server."

**Quickly open `src/pr_review_agent/adapters/slack_app.py`** — point at
`parse_command`, `build_review_blocks`, and the `@app.command("/review")`
handler. Ten seconds is enough.

### 2:20 – 2:45 — Impact
**Back to the Slack channel showing the findings.**

**Say:**
> "Why this matters in Slack. Reviewers don't have to leave the conversation
> where the decision is happening. The whole channel sees the findings.
> Hardcoded credentials, injection, unsafe `eval` — caught before merge, in
> the chat the team already lives in. MIT licensed, public repo, 49 tests
> passing in CI."

### 2:45 – 3:00 — Close
**On screen:** the GitHub repo page.

**Say:**
> "MergeGuard for Slack. Repo and setup guide linked below. Thanks for
> watching."

## Tips
- **Invite the bot to the channel first** (`/invite @PR Review Agent`) — done
  once, before you start recording.
- The Socket Mode connection on Windows is occasionally unstable; if `/review`
  ever returns *"app did not respond"*, restart the local app and try again
  fresh. Record only the successful take.
- If you want a longer / glossier demo, run the bot pointing at Vertex +
  Gemini 3.1 Pro instead of `gemini-2.5-flash` — set `PR_REVIEW_MODEL=
  gemini-3.1-pro-preview` before launching the app. (Costs trial credits, but
  the findings are richer.)
