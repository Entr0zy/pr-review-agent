# Devpost submission text — Google Cloud Rapid Agent Hackathon

Paste each block into the corresponding Devpost field. Edit the **Try it out**
links once your hosted URL and YouTube video link exist.

---

## Project name (40-char limit)
```
MergeGuard
```

## Tagline (one line)
```
An autonomous code-review agent on Google Cloud Agent Builder, powered by Gemini 3 + the GitLab MCP.
```

## Cover image / logo
A simple square graphic with the name **MergeGuard** and a shield+merge-icon
mark works fine. Skip if short on time; the architecture diagram is enough.

---

## Project story (full Devpost description — paste as-is)

```markdown
## Inspiration
Code review is the bottleneck on every team I've worked with. Reviewers spend
hours each week on diffs and still miss real security bugs because attention
runs out. Hardcoded secrets get merged. SQL formatting slips through. An
unsafe `eval()` lands in production. Reviewers aren't lazy — they're tired.

I wanted to know: can a Gemini 3 agent catch *the bugs that humans miss most*,
on every merge request, automatically, with explicit human approval before it
posts anything?

MergeGuard is the answer.

## What it does
MergeGuard is an autonomous code-review agent built on Google Cloud Agent
Builder and Gemini 3.1 Pro. Drop a merge request URL in, and the agent:

1. Fetches the diff through GitLab's official **MCP server**.
2. Sends each changed file through **Gemini 3.1 Pro on Vertex AI**, constrained
   to a strict JSON output schema with severity, file, exact line, and a fix
   suggestion.
3. Summarizes the findings ordered by severity, asks the user to approve, and
   only then posts the review back to the GitLab merge request as a note.

Three categories of bugs it reliably catches before merge:
- **Leaked credentials** — hardcoded keys, tokens, passwords.
- **Injection vulnerabilities** — SQL `%s` formatting, command injection.
- **Unsafe dynamic execution** — `eval`, `exec`, deserialization gadgets.

## How I built it
**Architecture (`docs/architecture.md` in the repo):**
- A platform-agnostic **review engine** (pure stdlib): diff parser → prompt
  builder → pluggable LLM → structured findings mapped to file lines.
- **Sources** fetch diffs (GitHub REST API and GitLab REST API today; the
  Google Cloud build wraps GitLab's MCP server inside the ADK toolset).
- **Adapters** post results to where they're useful: GitLab MR notes, Slack
  channel via Block Kit, a GitHub Check Run via the GitHub App webhook.

**Google Cloud stack:**
- **Gemini 3.1 Pro** (`gemini-3.1-pro-preview` via Vertex AI on the `global`
  location) is the brain. The structured-output `response_schema` constrains
  the model to a precise JSON shape with severity / file / line / detail /
  suggestion, so parsing is trivial and findings always land in the right
  place in the diff.
- **Google Cloud Agent Builder / ADK.** A deployable `root_agent` lives in
  `agents/gitlab_reviewer/agent.py`. It runs locally under `adk web agents`
  and deploys to Vertex Agent Engine unchanged.
- **GitLab MCP** (partner). The ADK agent connects to GitLab's official MCP
  server at `https://gitlab.com/api/v4/mcp` as a toolset. The model uses MCP
  tools to look up merge-request metadata, fetch the diff, and (after explicit
  user approval) post a review note back to the MR.

**Safety rails:** the agent's instruction tells it to treat all source text
and MR descriptions as **untrusted content** — never to follow instructions
embedded inside code or comments that would alter its review policy, leak
secrets, or trigger unrelated GitLab actions. Every write action requires
explicit user approval first.

## Challenges I ran into
- **Vertex AI model naming.** The published `gemini-3-pro-preview` id was
  retired during preview; the current id is `gemini-3.1-pro-preview` and it's
  only available in the `global` location, not regional ones. Listed the live
  models from `genai.Client(...).models.list()` to find what my project
  actually had access to, then pinned the right id in the agent factory.
- **MCP transport reliability.** The default Slack socket-mode transport was
  unstable on my development machine — I learned to ship the working core,
  then chase reliability with a documented fallback.
- **Push protection saved my skin.** GitHub's secret scanning blocked a push
  when a local `.env.bak-…` backup file slipped past my `.gitignore`. Caught
  on my workstation, not in public — `.gitignore` now covers `.env.*`,
  `gcp-vertex-key.json`, and the ADK session state.

## Accomplishments I'm proud of
- **49 unit tests, all green in CI.** The forge-agnostic core is fully tested
  without any cloud dependency.
- **Real reviews on real merge requests.** Gemini 3.1 Pro on this PR caught a
  SQL injection at the exact line and an `eval`-based RCE with a concrete fix
  suggestion (use a dispatch dict, not `eval`).
- **One core, five surfaces.** The same review engine powers a CLI, a GitHub
  Action, a Slack `/review` bot, an Agent Builder root agent, and a GitHub
  App webhook handler — without copy-pasting code between them.

## What I learned
- **Structured output is non-negotiable.** Passing a `response_schema` to
  Gemini 3 turns a flaky text-parse step into a deterministic pipeline.
- **MCP composes really well with ADK.** Treating GitLab MCP as a toolset
  inside the ADK agent meant zero glue code for tool dispatch.
- **Human-in-the-loop write gates change the trust model.** The agent is far
  more useful when it summarizes proposed write actions and waits — judges
  see the review, the author keeps control.

## What's next
- **Inline review comments** mapped to specific diff hunks (not just a single
  summary note).
- **GitHub PR posting parity** (we already verify webhook signatures + parse
  PR payloads — wiring the review POST is the next commit).
- **Repo-level config** (`.mergeguard.yml`) so teams pick which severities
  block, which scopes to ignore, and which models to use per environment.
```

---

## Built With (Devpost tags — add each as a tag)
```
gemini
gemini-3
vertex-ai
google-cloud
google-adk
agent-builder
mcp
gitlab
python
slack
github-actions
```

## Try it out (three links — fill in the ones you have)
- **GitHub repo:** https://github.com/Entr0zy/pr-review-agent
- **Hosted URL:** *(deploy the ADK agent to Cloud Run / Vertex Agent Engine,
  then paste the URL here — the hackathon requires this)*
- **Demo video (unlisted YouTube):** *(paste the link from your recording)*

## Tracks / categories (select on Devpost)
- Pick the **GitLab partner track** — we use the GitLab MCP as the partner
  integration, which is explicitly called out in the hackathon resources.

## Submission deadline
**Jun 11, 2026 @ 2:00pm PDT** — set yourself a calendar alarm 24h before.

---

## Last-mile checklist before you hit Submit
- [ ] Public GitHub repo with an **OSS license** (✅ MIT — already in repo).
- [ ] Working README with **quickstart** and **architecture diagram** (✅).
- [ ] **Hosted URL** of the deployed agent (Cloud Run or Agent Engine) — TODO.
- [ ] **~3-min YouTube video, Unlisted** — follow `docs/rapid-agent-demo-script.md`.
- [ ] All three required techs visible in the submission: **Gemini 3** ✅,
      **Agent Builder / ADK** ✅, **partner MCP (GitLab)** ✅.
- [ ] Acknowledged 18+ / eligible country (you're UK — eligible).
