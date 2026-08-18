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
cp .env.example .env
npm run dev
```

Open `http://localhost:5173`.

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

Frontend builds to a static bundle (Render Static Site); backend runs as a
Render Web Service against MongoDB Atlas.

**Backend env:** `MONGODB_URI`, `MONGODB_DB`, `GOOGLE_CLIENT_ID`,
`GOOGLE_CLIENT_SECRET`, `SESSION_SECRET`, `FRONTEND_URL`, `BACKEND_URL`,
`ENVIRONMENT=production`.

**Frontend env:** `VITE_API_BASE_URL`, `VITE_GOOGLE_CLIENT_ID`.

Because the deployed frontend and API sit on different sites, the session
cookie is issued with `SameSite=None; Secure` outside local — which is why CSRF
protection is not optional here.

On Render's free tier the service spins down when idle. The client treats
502/503/504 and connection failures as transient and retries with backoff
behind a "waking the server" state rather than surfacing an error.

`.env` is never committed.
