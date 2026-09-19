export type Difficulty = "beginner" | "intermediate" | "advanced";
export type WorkoutSource = "random" | "ai";

export type User = {
  id: number;
  email: string;
  name: string | null;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer" | string;
};

export type WorkoutExercise = {
  exercise_id: number;
  name: string;
  illustration_slug: string;
  sets: number;
  reps: string;
  rest_seconds: number;
  notes: string | null;
};

export type WorkoutPlan = {
  title: string;
  duration_minutes: number;
  difficulty: Difficulty;
  source: WorkoutSource;
  exercises: WorkoutExercise[];
};

export type HistoryEntry = {
  id: number;
  workout_plan: WorkoutPlan;
  completed_at: string;
  notes: string | null;
  created_at: string;
};

export const ILLUSTRATION_SLUGS = [
  "row",
  "press",
  "squat",
  "lunge",
  "plank",
  "twist",
  "curl",
  "pull",
  "chest-fly",
  "core-crunch",
  "hinge",
  "jump",
  "stretch",
  "default",
] as const;

export type IllustrationSlug = (typeof ILLUSTRATION_SLUGS)[number];
