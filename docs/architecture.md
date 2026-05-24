# Architecture

`pr-review-agent` keeps a small, dependency-free **review engine** separate from
**sources** (where diffs come from) and **adapters** (where it runs). The same
engine powers every hackathon target and the eventual GitHub Marketplace app.

## Components

```mermaid
flowchart LR
    subgraph sources
      GH[GitHub REST API]
      GL[GitLab MCP server]
      STDIN[git diff / stdin]
    end

    DIFF[unified diff text] --> P[diff_parser]
    GH --> DIFF
    GL --> DIFF
    STDIN --> DIFF

    P --> PR[prompts]
    PR --> LLM{LLMClient}
    LLM -->|Gemini 3 + JSON schema| J[findings JSON]
    LLM -->|Heuristic - offline| J
    J --> R[ReviewResult]

    subgraph adapters
      GC[Google Cloud Agent Builder]
      SL[Slack app]
      GHA[GitHub App / Marketplace]
    end
    R --> GC
    R --> SL
    R --> GHA
```

## Review sequence

```mermaid
sequenceDiagram
    participant User
    participant Source as Source (GitHub/GitLab/stdin)
    participant Engine as PRReviewer
    participant LLM as LLMClient (Gemini)
    User->>Source: PR / MR reference
    Source-->>Engine: unified diff text
    Engine->>Engine: parse diff -> per-file, line-numbered
    loop per file (or batched)
        Engine->>LLM: system + rendered diff
        LLM-->>Engine: findings JSON (schema-constrained)
    end
    Engine-->>User: ReviewResult (findings + summary, exit code)
```

## Module map

| Module | Responsibility |
|---|---|
| `diff_parser` | unified diff -> `FileDiff` with new-file line numbers |
| `prompts` | system prompt, per-file & batch prompts, `RESPONSE_SCHEMA` |
| `reviewer.PRReviewer` | orchestration; per-file or batched; lenient JSON parse |
| `llm/gemini` | Gemini backend with structured-output schema |
| `llm/mock` | offline `MockLLMClient` (tests) + `HeuristicLLMClient` (demo) |
| `sources/github` | fetch a PR diff via the GitHub REST API (stdlib) |
| `adapters/*` | per-platform glue (Google Cloud, Slack, GitHub App) |

**Why this shape:** each hackathon mandates a different orchestration layer, so
all platform specifics live in `adapters/` and the reusable logic stays in
`reviewer` + `prompts` + `diff_parser` (zero third-party deps).
