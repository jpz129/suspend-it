import type { HistoryEntry, User, WorkoutPlan } from "../types/api";

const now = "2026-01-01T00:00:00Z";

export const mockUser: User = {
  id: 1,
  email: "demo@suspend.it",
  name: "Demo Athlete",
  created_at: now,
};

export const mockPlan = (source: WorkoutPlan["source"], title: string): WorkoutPlan => ({
  title,
  duration_minutes: 30,
  difficulty: "beginner",
  source,
  exercises: [
    {
      exercise_id: 1,
      name: "TRX Row",
      illustration_slug: "row",
      sets: 3,
      reps: "10",
      rest_seconds: 45,
      notes: "Squeeze the shoulder blades",
    },
    {
      exercise_id: 2,
      name: "TRX Squat",
      illustration_slug: "squat",
      sets: 3,
      reps: "12",
      rest_seconds: 45,
      notes: null,
    },
    {
      exercise_id: 3,
      name: "TRX Plank",
      illustration_slug: "plank",
      sets: 3,
      reps: "30s",
      rest_seconds: 30,
      notes: "Brace the core",
    },
  ],
});

export const mockHistory: HistoryEntry[] = [
  {
    id: 1,
    workout_plan: mockPlan("random", "Yesterday's draw"),
    completed_at: "2026-01-02T00:00:00Z",
    notes: null,
    created_at: "2026-01-02T00:05:00Z",
  },
];
