# Napkin Chain

**Build systems on a napkin.**

A system-design estimation trainer for engineers. Instead of disconnected
quiz questions, you solve a real system as a *chain* of estimates, where every
number you produce becomes the input to the next one:

```
100M DAU → 1B requests/day → 10K QPS → 30K peak QPS → bandwidth → storage → servers
```

Estimates are scored on **order of magnitude**, not exact arithmetic. When you
miss a step, the product sends you to the one concept behind it and returns you
to the exact step you left.

---

## Architecture

Three things are kept deliberately separate, because they evolve at different
speeds:

| Concern | Owner | Collections |
| --- | --- | --- |
| What a challenge **is** | `seed/`, `models/challenge.py` | `challenges`, `concepts` |
| What the user **did** | `services/attempt_service.py` | `challenge_attempts`, `node_attempts` |
| What we believe they **know** | `services/mastery_service.py` | `concept_progress` |

Evaluation and mastery are pure functions with no database access, so both are
tested directly. Nothing user-scoring related is ever accepted from the client:
the server computes ratios, classifications and mastery, and expected answers
are not serialised to the browser until a node has been attempted.

```
backend/app/
  api/        route handlers (thin)
  services/   business logic
  models/     Pydantic documents, each with an explicit schemaVersion
  schemas/    API view models (camelCase)
  db/         motor connection + deliberate indexes
  core/       config, security, structured logging
  seed/       challenge and concept content

frontend/src/
  routes/     one file per screen
  components/chain/      the napkin: DAG layout, canvas, mobile strip/sheet
  components/workspace/  estimate input and feedback
  components/napkin/     handwritten notes, hand-drawn marks
  lib/        API client, formatting, query client
  stores/     unsent draft state (localStorage-backed)
```

## Running it locally

You need Node 20+, Python 3.12+, and a MongoDB connection string.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then fill in MONGODB_URI at minimum
python -m app.seed.run      # loads challenges and concepts, creates indexes
uvicorn app.main:app --reload
```

API docs at `http://localhost:8000/docs` (disabled in production).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to the backend, so the browser
sees a single origin in development exactly as it does in production — no
`VITE_API_BASE_URL` needed unless you deliberately split the deployment.

### Signing in without Google credentials

With `ENVIRONMENT=local`, the login screen exposes a development sign-in that
creates a real user without contacting Google. The endpoint returns 404 in any
other environment.

To use real Google sign-in, set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` and
register `http://localhost:8000/api/auth/google/callback` as an authorized
redirect URI.

## Health checks

```
GET /health      → {"status": "ok"}          liveness, never touches the database
GET /health/db   → {"status": "ok"|"error"}  database reachability, reported separately
```

## Tests

```bash
cd backend && .venv/bin/python -m pytest      # 51 tests
cd frontend && npm test                       # 28 tests
```

Backend covers the evaluation engine, mastery scoring, authorization, and the
full challenge flow end to end against a real database (skipped automatically
when none is reachable). Frontend covers estimate parsing, chain layout, the
estimate/feedback panels, and the workspace's fail → learn → retry loop.

## Security notes

- Google identity is validated server-side against Google's JWKS; the OAuth
  access token is discarded once the identity is confirmed.
- The application session is a short-lived signed JWT in an `HttpOnly` cookie,
  `Secure` outside local, with a double-submit CSRF token on every mutation.
- Every user-scoped query is filtered by the session's user id. A `userId` in a
  request body is ignored.
- Auth and submission endpoints are rate limited per client. The limiter is
  in-process — move it to a shared store before running more than one instance.

## Deployment

`render.yaml` deploys **one** Render web service that serves both the API and
the built SPA, against MongoDB Atlas.

One service, not two, on purpose. Render gives each service its own
`*.onrender.com` subdomain, and `.onrender.com` is a public-suffix domain — so
a split deployment would make the session cookie *third-party*, which Safari
blocks outright and Chrome increasingly does too. Users would sign in and be
immediately signed out. Serving both halves from one origin keeps the cookie
first-party with `SameSite=Lax`, and removes CORS entirely.

The split configuration still works (`SERVE_FRONTEND=false` with distinct
`FRONTEND_URL`/`BACKEND_URL`) and falls back to `SameSite=None; Secure` plus a
CORS allow-list — but only put it behind same-site subdomains of a real domain.

### Deploying

1. Render → **New → Blueprint** → pick this repo. It reads `render.yaml`.
2. Paste `MONGODB_URI` when prompted. `SESSION_SECRET` is generated by Render.
3. Deploy. The app runs immediately; sign-in is disabled until step 4.
4. Create a Google OAuth **Web application** client with the deployed URL:
   `https://<service>.onrender.com/api/auth/google/callback` as an authorized
   redirect URI. Publish the consent screen — with only `openid`/`email`/
   `profile` scopes there is no verification review, and leaving it in Testing
   caps you at 100 manually-added addresses. Put the Client ID and Secret into
   Render's environment and redeploy.

Atlas needs Network Access set to `0.0.0.0/0`: free Render instances have no
static outbound IP, so the database user's password is the access control.

The service URL is read from `RENDER_EXTERNAL_URL` at runtime, so it never has
to be pasted back in after the first deploy.

### Free-tier behaviour

Free instances sleep after ~15 minutes idle and take roughly a minute to wake.
The client treats 502/503/504 and connection failures as transient, retrying
with backoff behind a "waking the server" state instead of showing an error.

To avoid the wait, point a free uptime monitor at `/health` every 10 minutes —
that endpoint deliberately never touches the database. Note that staying awake
around the clock consumes most of a month's free instance hours, which is the
other reason this is a single service rather than two.

Free instances also have no shell, so content is seeded idempotently on startup
rather than by a manual command.

`.env` is never committed, and no secret is ever stored in the repo.
