# AGENTS.md — TRX/Suspension Trainer Workout App

Instructions for coding agents (e.g. Cursor sub-agents) building this app.
The architecture is split into 5 independent components (A-E) with fixed
file ownership and fixed interfaces between them, so they can be built in
parallel, on separate branches, without agents needing to read each
other's code — only this document.

## 1. Project overview

A mobile app for TRX/suspension-trainer workouts.

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite by default (swap to
  Postgres via `DATABASE_URL` alone — no code change needed).
- **Mobile**: React Native + Expo, TypeScript.
- **Exercise data**: [wger](https://wger.de) public API (free, no key) for
  exercise text metadata, plus a curated TRX-specific seed list, because no
  free exercise API tags exercises for suspension trainers specifically.
- **Visuals**: no exercise API reliably covers suspension training, and
  AI-generated video is unreliable for depicting correct exercise form. So
  exercises use **static illustrated cards** (simple line-art figure on a
  colored card, similar to physical suspension-training card decks)
  instead of photos/video. A small fixed set of generic pose illustrations
  is used as placeholders — swappable later for polished/per-exercise art
  with zero code changes (see Component B).
- **AI workouts**: [LiteLLM](https://github.com/BerriAI/litellm) calling
  Anthropic (Claude) by default, returning the same structured JSON shape
  as the random generator so the UI renders both identically.
- **Auth**: email + password, JWT bearer tokens. Workout history is
  per-user, so accounts are required.
- **Attribution**: wger exercise data is CC-BY-SA — show a small
  attribution line ("Exercise data from wger.de") somewhere in the app
  (e.g. a settings/about screen).

## 2. Repo layout

```
suspend-it/
  backend/
    app/
      main.py
      core/            # config.py, security.py
      db/              # session.py
      models/          # user.py, exercise.py, history.py
      schemas/         # workout.py, etc.
      api/routes/      # auth.py, exercises.py, workouts.py, ai_workouts.py, history.py
      services/        # exercise_ingest.py, workout_generator.py, ai_workout.py
      data/            # trx_seed.json
    static/illustrations/   # <slug>.svg pose placeholders
    scripts/ingest_exercises.py
    alembic/
    requirements.txt
    .env.example
  mobile/
    (Expo app; screens, navigation, API client)
  AGENTS.md
  README.md
```

## 3. API contract

All authenticated endpoints require `Authorization: Bearer <token>`.
Errors use FastAPI's default shape: `{"detail": "..."}`.

### Auth

`POST /auth/register`
```json
// request
{ "email": "string", "password": "string", "name": "string | null" }
// response 201
{ "id": 1, "email": "string", "name": "string | null", "created_at": "2026-01-01T00:00:00Z" }
```

`POST /auth/login`
```json
// request
{ "email": "string", "password": "string" }
// response 200
{ "access_token": "string", "token_type": "bearer" }
```

`GET /auth/me` (auth required) → same shape as register's response.

### Exercises

`GET /exercises?muscle_group=&difficulty=&equipment=&search=` (all filters optional)
```json
// response 200
[
  {
    "id": 1,
    "name": "TRX Row",
    "muscle_group": "back",
    "difficulty": "beginner",
    "equipment": "suspension trainer",
    "instructions": "string",
    "illustration_slug": "row",
    "source": "curated"
  }
]
```

`GET /exercises/{id}` → single object of the same shape.

### Shared `WorkoutPlan` schema

Used as the response body for both the random generator and the AI
endpoint, and embedded in history entries. Mobile renders both the same
way because the shape is identical.

```json
{
  "title": "string",
  "duration_minutes": 30,
  "difficulty": "beginner | intermediate | advanced",
  "source": "random | ai",
  "exercises": [
    {
      "exercise_id": 1,
      "name": "TRX Row",
      "illustration_slug": "row",
      "sets": 3,
      "reps": "10",
      "rest_seconds": 45,
      "notes": "string | null"
    }
  ]
}
```

### Workouts

`POST /workouts/generate` (auth required)
```json
// request
{ "duration_minutes": 30, "muscle_groups": ["back", "legs"], "difficulty": "beginner" }
// response 200: WorkoutPlan (source="random")
```

`POST /workouts/ai-generate` (auth required)
```json
// request
{ "goals": "string", "available_time_minutes": 20, "equipment": ["TRX"], "notes": "string | null" }
// response 200: WorkoutPlan (source="ai")
```

### History

`POST /history` (auth required)
```json
// request
{ "workout_plan": /* WorkoutPlan */, "completed_at": "2026-01-01T00:00:00Z", "notes": "string | null" }
// response 201
{ "id": 1, "workout_plan": /* WorkoutPlan */, "completed_at": "...", "notes": "string | null", "created_at": "..." }
```

`GET /history` (auth required) → array of the same shape as `POST /history`'s response, newest first.

## 4. Component breakdown

Each component lists what it owns, what it exposes for others to import,
and what it depends on. **Only read the interface listed for a dependency
— not that component's implementation.**

### A. Backend core & auth
- **Owns**: `app/main.py` (skeleton only — see §7), `app/core/`, `app/db/`,
  `app/models/user.py`, `app/api/routes/auth.py`.
- **Exposes**: `app.core.security.get_current_user` — a FastAPI dependency
  that returns the authenticated `User` (or raises 401). Every other
  route that needs auth imports this by name.
- **Depends on**: nothing.

### B. Exercise data & illustrations
- **Owns**: `app/models/exercise.py`, `app/services/exercise_ingest.py`,
  `app/data/trx_seed.json`, `static/illustrations/`,
  `app/api/routes/exercises.py`, `scripts/ingest_exercises.py`.
- **Exposes**: the `Exercise` SQLAlchemy model at `app.models.exercise`,
  with columns: `id, name, muscle_group, difficulty, equipment,
  instructions, illustration_slug, source, external_id`. This is the fixed
  interface Component C queries against.
- **Ingestion**: fetch from wger `/api/v2/exercise/` (paginated, filtered
  to bodyweight/no-equipment categories), merge `app/data/trx_seed.json`
  (curated list, `source="curated"`), upsert by
  `(source, external_id_or_name)` — idempotent. Runs via
  `scripts/ingest_exercises.py`, **not** on every app boot (keep the app
  usable offline and avoid API rate limits).
- **Illustration slugs** — use exactly these, do not invent new ones (so
  Component E's bundled assets and B's ingestion mapping never drift):
  `row`, `press`, `squat`, `lunge`, `plank`, `twist`, `curl`, `pull`,
  `chest-fly`, `core-crunch`, `hinge`, `jump`, `stretch`, `default`
  (fallback for anything unmapped). Each is a simple placeholder SVG at
  `static/illustrations/<slug>.svg` — a basic line-art figure on a colored
  card background, in the spirit of physical suspension-trainer exercise
  card decks. Not per-exercise-accurate art; a drop-in placeholder. Map
  each ingested exercise to the closest slug using
  category/muscle-group/name keywords; curated seed entries get the slug
  hand-assigned at authoring time.
- **Depends on**: nothing. Can be built and tested fully standalone.

### C. Workout generation (random + AI)
- **Owns**: `app/schemas/workout.py` (the `WorkoutPlan` Pydantic schema,
  matching §3 exactly), `app/services/workout_generator.py`,
  `app/services/ai_workout.py`, `app/api/routes/workouts.py`,
  `app/api/routes/ai_workouts.py`.
- **Random generator**: filter `Exercise` rows by muscle
  group(s)/difficulty, randomly sample enough to fill
  `duration_minutes`, apply a difficulty → sets/reps/rest heuristic table
  (e.g. beginner: 2 sets/10 reps/45s rest; advanced: 4 sets/15 reps/30s
  rest — pick reasonable values, this is not user-configurable in v1).
- **AI generator**: call `litellm.completion()` targeting Anthropic, with
  a system prompt that requires JSON output matching `WorkoutPlan`
  exactly; validate the response with the Pydantic schema and retry once
  on parse failure before erroring.
- **Depends on**: A's `get_current_user`, B's `Exercise` model/columns
  (import only, don't reimplement).

### D. History
- **Owns**: `app/models/history.py`, `app/api/routes/history.py`.
- Persists a `WorkoutPlan` (as JSON) per completed workout, tied to the
  authenticated user, with `completed_at` and optional `notes`.
- **Depends on**: A's `get_current_user`, C's `WorkoutPlan` schema.

### E. Mobile app
- **Owns**: all of `mobile/`.
- **Screens**: Login/Register, Home, Draw-a-Card (filters: duration,
  muscle groups, difficulty → calls `POST /workouts/generate`; reveals
  exercises with a card-flip animation, each card showing its
  illustration + name/sets/reps), AI Workout (goal/time/equipment form →
  calls `POST /workouts/ai-generate`; renders results with the same card
  component as Draw-a-Card since the shape is identical), Workout Player
  (checklist through the plan's exercises, then `POST /history` on
  finish), History (list from `GET /history`).
- **Stack**: Expo managed workflow, React Navigation (stack + bottom
  tabs), TanStack Query for data fetching, `expo-secure-store` for the JWT,
  `react-native-reanimated` for the card-flip animation. Minimal, neutral
  UI — few screens, no extra chrome.
- **Depends on**: only the API contract in §3. Build against a local mock
  server or hardcoded fixtures matching that contract — do not wait on
  A-D to be finished first.

## 5. Setup notes

**Backend dependencies** (pin these, don't substitute):
`fastapi`, `uvicorn`, `sqlalchemy>=2.0`, `alembic`, `pydantic-settings`,
`passlib[bcrypt]`, `python-jose[cryptography]` (JWT), `httpx` (wger calls),
`litellm`, `pytest`.

**Mobile dependencies**: Expo SDK (latest stable),
`@react-navigation/native` (+ native-stack and bottom-tabs),
`@tanstack/react-query`, `expo-secure-store`, `react-native-reanimated`.

**Env vars** (`backend/.env.example`):
```
DATABASE_URL=sqlite:///./app.db
JWT_SECRET=change-me
ANTHROPIC_API_KEY=
WGER_API_BASE=https://wger.de/api/v2
```

**Run backend**: `cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --reload`

**Run ingestion**: `cd backend && python scripts/ingest_exercises.py`

**Run mobile**: `cd mobile && npm install && npx expo start`

## 6. Definition of done per component

- **A**: register → login → `GET /auth/me` round-trip works; passwords
  are hashed, not stored plaintext; invalid/missing token returns 401.
- **B**: ingestion script runs twice without creating duplicates; every
  exercise row has a non-null `illustration_slug` that resolves to a real
  file in `static/illustrations/`.
- **C**: `POST /workouts/generate` returns a valid `WorkoutPlan` for
  varied filter combinations (including ones with few matching
  exercises); `POST /workouts/ai-generate` returns a valid `WorkoutPlan`
  or a clear error if the LLM output doesn't validate after one retry.
- **D**: `POST /history` then `GET /history` round-trips correctly and
  only returns the authenticated user's own entries.
- **E**: can complete the full flow (login → draw-a-card or AI workout →
  play through it → see it in history) against a running backend on a
  real device/simulator via Expo Go.

## 7. Coordination for parallel agents

Components are designed to touch disjoint files so agents can work in
parallel on separate branches. The one shared file, `app/main.py`, is
**not owned by any component** — agents should leave their router
registration as a one-line TODO comment in their own route file (e.g.
`# TODO: register in app/main.py: app.include_router(auth_router)`)
rather than editing `main.py` directly. Wiring `main.py` (adding one
`include_router(...)` call per component) is a final, separate 5-minute
integration step done once after components are merged.
