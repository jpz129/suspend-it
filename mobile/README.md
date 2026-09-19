# suspend-it mobile

Expo managed app for TRX / suspension-trainer workouts.

## Run

```bash
cd mobile
npm install
npx expo start
```

Open in Expo Go. Mock mode is on by default (`EXPO_PUBLIC_USE_MOCKS=true`), so the full flow works without a backend:

login → draw-a-card or AI workout → play through the checklist → see it in History.

## Live backend

```bash
EXPO_PUBLIC_USE_MOCKS=false EXPO_PUBLIC_API_URL=http://<lan-ip>:8000 npx expo start
```

The typed client in `src/api/client.ts` matches AGENTS.md §3.

## Attribution

Exercise data from wger.de (CC-BY-SA), shown on the Settings/About tab.
