# Suspend It — mobile app (Component E)

Expo (SDK 57) + React Native + TypeScript client for TRX / suspension-trainer workouts.

Screens: login/register, home, draw-a-card, AI workout, workout player, history, settings/about.

## Run

```bash
cd mobile
npm install
npx expo start
```

Then open in Expo Go (phone) or a simulator.

Mock mode is **on by default**, so the full flow works without a backend:

1. Log in as `demo@suspend.it` / `password123` (prefilled) — or register any account.
2. Draw a card **or** generate an AI workout.
3. Flip the cards, start the workout, check off each exercise, finish.
4. Confirm it appears in **History**.

Attribution lives on **Settings**: `Exercise data from wger.de` (CC-BY-SA).

## Mock vs live API

| Env | Default | Meaning |
| --- | --- | --- |
| `EXPO_PUBLIC_USE_MOCKS` | `true` | In-client fixture adapter (same types as the real API) |
| `EXPO_PUBLIC_API_URL` | `http://localhost:8000` | Used when mocks are off |

Copy `.env.example` to `.env` if you want to change them:

```bash
# Demo without a backend (default)
EXPO_PUBLIC_USE_MOCKS=true

# Talk to a running backend instead
EXPO_PUBLIC_USE_MOCKS=false
EXPO_PUBLIC_API_URL=http://localhost:8000
```

Android emulator: use `http://10.0.2.2:8000` instead of localhost. A physical device needs your computer's LAN IP.

The typed client in `src/api/` is shared: `mockAdapter` vs `liveAdapter`. Switching is a URL + flag change — method names and `WorkoutPlan` shapes stay identical.

## Tests

```bash
cd mobile
npm test
```

Jest covers the mock adapter (auth, generate, AI generate, history isolation) and FastAPI error parsing.

## Illustrations

Placeholder PNGs for the fixed slug list live in `assets/illustrations/`. Mapped in `src/illustrations/` with a `default` fallback. Do not invent new slugs — they must stay in sync with Component B:

`row`, `press`, `squat`, `lunge`, `plank`, `twist`, `curl`, `pull`, `chest-fly`, `core-crunch`, `hinge`, `jump`, `stretch`, `default`

Regenerate with:

```bash
python3 scripts/generate_illustrations.py
```
