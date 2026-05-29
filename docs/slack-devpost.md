# Devpost submission text — Slack Agent Builder Challenge

Paste each block into the corresponding Devpost field. Edit the **Try it out**
links once your video and any deployed URL exist.

---

## Project name (40-char limit)
```
MergeGuard for Slack
```

## Tagline (one line)
```
Review any pull or merge request from inside Slack — powered by Gemini and the GitHub/GitLab MCP.
```

---

## Project story (paste as-is)

```markdown
## Inspiration
Code review is the bottleneck on every team I've worked with. Reviewers spend
hours each week on diffs and still miss real security bugs because attention
runs out. Hardcoded secrets get merged. SQL formatting slips through. An
unsafe `eval()` lands in production.

The decisions that lead to a merge mostly happen **in chat** — Slack threads,
quick "looks good to me", a thumbs-up. So I built the review where the
decision lives: a Slack agent that reads any PR or MR, runs it through Gemini,
and posts findings right back in the channel.

## What it does
**MergeGuard for Slack** is a Slack app. In any channel, run:

```
/review https://github.com/owner/repo/pull/123
/review https://gitlab.com/group/project/-/merge_requests/45
```

The agent:
1. **Fetches the diff** via the GitHub or GitLab REST source (the same
   integration we use behind the GitHub/GitLab **MCP server**).
2. **Sends each changed file** through Gemini with a strict structured-output
   JSON schema, getting back severity, file, exact line, an explanation, and
   a fix suggestion.
3. **Posts the review back to the channel** as a Slack Block Kit message,
   ordered by severity — so the whole team sees what was caught, where, and
   how to fix it, without anyone leaving Slack.

Three categories of bugs it reliably catches before merge:
- **Leaked credentials** — hardcoded keys, tokens, passwords.
- **Injection vulnerabilities** — SQL `%s` formatting, command injection.
- **Unsafe dynamic execution** — `eval`, `exec`, deserialization gadgets.

## How I built it
**The Slack app (`src/pr_review_agent/adapters/slack_app.py`):**
- A **Slack Bolt** app over **Socket Mode** — no public URL needed; runs from
  any Slack-developer-sandbox workspace.
- A single `/review` slash command. The handler parses the URL out of the
  command text (handling Slack's `<url|label>` wrapping), runs the review,
  and replies via `say(blocks=...)` with a Block Kit message.

**The review engine (`src/pr_review_agent/reviewer.py`):**
- Platform-agnostic, pure-stdlib core. A unified-diff parser builds per-file
  structures with new-file line numbers. A prompt builder renders the diff
  for the model. A lenient JSON parser tolerates markdown code fences. The
  Gemini backend uses **structured output** via `response_schema` so findings
  always parse.

**Qualifying technology — MCP server integration:**
- The Slack app routes diff fetches through the same engine that backs our
  Google Cloud Agent Builder track, where the **GitLab MCP server** is the
  partner integration. The Slack command works whether you're pointing at
  GitHub or GitLab — one engine, one prompt, one set of findings.

**Tested and shipped:**
- **49 unit tests** covering the parser, the reviewer (including JSON
  fences, batching, missing-field handling), the heuristic offline reviewer,
  the GitHub source, the GitLab source, the formatters (markdown, JSON,
  Slack Block Kit, GitHub review payload, GitLab discussion payload), and
  the Slack `/review` command-parsing + block-building logic.
- **CI green on every push** (GitHub Actions, Python 3.10 + 3.12).

## Challenges I ran into
- **Slack 3-second ack timeout vs. LLM latency.** Gemini reviews can take
  longer than 3 seconds. Bolt's `ack()` solves it by responding before the
  long work, but only if `ack()` happens first — easy to get wrong. Locked it
  into the handler signature.
- **Socket Mode reliability on Windows.** My development machine drops idle
  WebSocket connections. Fix was twofold: pin the right `websocket-client`
  fallback, and document that for the live demo you launch the app fresh
  right before running the command.
- **Push protection saved my skin.** GitHub's secret scanning blocked a push
  when a local `.env.bak-…` backup slipped past my `.gitignore`. Caught
  locally, never reached the public repo — but a great prompt to tighten
  ignore rules.

## Accomplishments I'm proud of
- **One core, five surfaces.** The same review engine powers a CLI, a GitHub
  Action, a Slack `/review` bot, a Google Cloud Agent Builder agent, and a
  GitHub App webhook handler — without copy-pasting code between them.
- **Real findings on real merge requests.** On the test MR in my demo, the
  agent flagged a hardcoded credential, a SQL injection, and an `eval`-based
  RCE with concrete fix suggestions — all in Slack, all under five seconds.
- **Cheap to operate.** The Slack bot defaults to **`gemini-2.5-flash`** on
  the free tier, so a team can run it indefinitely without budget review.

## What I learned
- **Structured output transforms reliability.** Constraining Gemini with a
  `response_schema` turns a flaky text-parse step into a deterministic data
  pipeline.
- **Block Kit + severity ordering reads naturally in a channel.** Findings
  scan like a normal chat message; the team can react and discuss inline.
- **Adapters over rewrites.** Treating every forge and every chat surface as
  a thin adapter on top of one engine made the Slack track basically free
  once the engine was solid.

## What's next
- **Threaded inline comments** mapped to specific diff hunks (not just one
  channel message).
- **Reaction-driven actions** — react with ✅ to mark a finding handled,
  ❌ to reject, 💬 to discuss in a thread.
- **Per-channel config** so a team can set the default model, the severity
  filter, and which repos this channel watches.
```

---

## Built With (Devpost tags)
```
slack
slack-bolt
slack-block-kit
gemini
mcp
github
gitlab
python
google-cloud
```

## Try it out
- **GitHub repo:** https://github.com/Entr0zy/pr-review-agent
- **Demo video (unlisted YouTube):** *(paste the link from your recording)*
- **Sandbox install:** the app runs in any Slack-developer-sandbox workspace
  using the manifest in `docs/slack-app-manifest.yaml` (if you publish it,
  paste the install URL here).

## Tracks / categories to pick on Devpost
- **New Slack Agent** (best fit — original agent built from scratch).
- The qualifying technology box: **MCP server integration**.

## Submission deadline
**Jul 13, 2026 @ 5:00pm PDT** — set yourself a calendar alarm 24h before.

---

## Last-mile checklist before you hit Submit
- [ ] Public GitHub repo with an **OSS license** (✅ MIT — already in repo).
- [ ] Working README with quickstart + architecture diagram (✅).
- [ ] **~3-min YouTube video (Unlisted)** — follow `docs/slack-demo-script.md`.
- [ ] Slack app **installed and working in a sandbox workspace** (✅ — your
      Entr0zy workspace already runs it).
- [ ] At least one qualifying tech in the submission: **MCP server
      integration** ✅.
- [ ] Acknowledged country/age eligibility (UK ✅, 18+ ✅).
