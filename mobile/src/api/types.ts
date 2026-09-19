export type Difficulty = 'beginner' | 'intermediate' | 'advanced';
export type WorkoutSource = 'random' | 'ai';

export type User = {
  id: number;
  email: string;
  name: string | null;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: 'bearer';
};

export type RegisterRequest = {
  email: string;
  password: string;
  name: string | null;
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type PlannedExercise = {
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
  exercises: PlannedExercise[];
};

export type GenerateWorkoutRequest = {
  duration_minutes: number;
  muscle_groups: string[];
  difficulty: Difficulty;
};

export type AiGenerateRequest = {
  goals: string;
  available_time_minutes: number;
  equipment: string[];
  notes: string | null;
};

export type SaveHistoryRequest = {
  workout_plan: WorkoutPlan;
  completed_at: string;
  notes: string | null;
};

export type HistoryEntry = {
  id: number;
  workout_plan: WorkoutPlan;
  completed_at: string;
  notes: string | null;
  created_at: string;
};

export type ApiClient = {
  register: (body: RegisterRequest) => Promise<User>;
  login: (body: LoginRequest) => Promise<TokenResponse>;
  me: (token: string) => Promise<User>;
  generateWorkout: (token: string, body: GenerateWorkoutRequest) => Promise<WorkoutPlan>;
  generateAiWorkout: (token: string, body: AiGenerateRequest) => Promise<WorkoutPlan>;
  saveHistory: (token: string, body: SaveHistoryRequest) => Promise<HistoryEntry>;
  listHistory: (token: string) => Promise<HistoryEntry[]>;
};
