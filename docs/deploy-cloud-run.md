# Deploy the agent to Google Cloud Run

The Rapid Agent submission asks for a **hosted URL** judges can hit. This is
the shortest path: deploy the ADK `root_agent` to Cloud Run with one command,
using your existing `entr0zy-youtube` project + free trial credit.

## Prereqs you already have
- `entr0zy-youtube` GCP project with billing active and £222 trial credit.
- Service account `pr-review-agent@entr0zy-youtube.iam.gserviceaccount.com`
  with Vertex AI access.
- `.env` set up locally with `GOOGLE_CLOUD_PROJECT=entr0zy-youtube` and
  `GOOGLE_GENAI_USE_VERTEXAI=TRUE`.
- The public GitHub repo with the ADK agent at `agents/gitlab_reviewer/`.

## One-time setup (~10 min)

### 1. Install gcloud CLI (Windows)
Download and run the installer from
**https://cloud.google.com/sdk/docs/install#windows** — keep all defaults,
tick **"Run gcloud init"** at the end.

### 2. Authenticate + pick the project
`gcloud init` opens a browser. Sign in with the **same Google account** that
owns `entr0zy-youtube` and pick that project when prompted. Then:

```bash
gcloud auth application-default login
```
Another browser prompt — sign in again, allow access.

### 3. Enable the APIs Cloud Run needs
Paste this whole block:
```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  --project=entr0zy-youtube
```

### 4. Grant Cloud Run's default service account access to Vertex
```bash
PROJECT_NUMBER=$(gcloud projects describe entr0zy-youtube --format='value(projectNumber)')
gcloud projects add-iam-policy-binding entr0zy-youtube \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## Deploy (~3 min, one command)

ADK ships a Cloud Run deploy command. From the repo root:

```bash
adk deploy cloud_run \
  --project=entr0zy-youtube \
  --region=us-central1 \
  --service_name=mergeguard \
  agents/gitlab_reviewer
```

It builds a container, pushes to Artifact Registry, and deploys to Cloud Run.
When it finishes you'll see a URL like:
```
Service URL: https://mergeguard-xxxxxxxxxx-uc.a.run.app
```

That's your **hosted URL** for the Devpost submission.

## Set the env vars Cloud Run needs at runtime

The deployed service needs to know it's using Vertex + which project/location.
After the first deploy, set them once:

```bash
gcloud run services update mergeguard \
  --project=entr0zy-youtube --region=us-central1 \
  --set-env-vars=GOOGLE_GENAI_USE_VERTEXAI=TRUE,GOOGLE_CLOUD_PROJECT=entr0zy-youtube,GOOGLE_CLOUD_LOCATION=global,PR_REVIEW_MODEL=gemini-3.1-pro-preview
```

If your agent also needs the GitLab MCP auth token at runtime, add:
`,GITLAB_MCP_AUTH_TOKEN=<token>` to the same `--set-env-vars` flag.

## Smoke-test the hosted agent
```bash
curl https://mergeguard-xxxxxxxxxx-uc.a.run.app/health
```
Should return a 200. Then open the URL in a browser — ADK's deployed agent
serves a simple Web UI by default.

## Costs (you're on free credits)
- Cloud Run has a generous always-free tier (2M requests/month). For a hackathon
  demo it's effectively zero.
- Gemini 3.1 Pro calls bill against your **£222 free trial credit** — a 3-min
  demo and judge testing won't dent it.

## Roll back / nuke if you mess up
```bash
gcloud run services delete mergeguard --region=us-central1 --project=entr0zy-youtube
```

## Drop the hosted URL into the submission
- Paste the URL into the **"Try it out"** field on `docs/rapid-agent-devpost.md`,
  then into the Devpost form.
- Mention the URL in the demo video close ("…live deployment at this URL").
