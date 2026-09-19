import { ApiError } from './errors';
import { DEMO_USER, FIXTURE_EXERCISES, type FixtureExercise } from './fixtures';
import type {
  AiGenerateRequest,
  ApiClient,
  Difficulty,
  GenerateWorkoutRequest,
  HistoryEntry,
  LoginRequest,
  PlannedExercise,
  RegisterRequest,
  SaveHistoryRequest,
  TokenResponse,
  User,
  WorkoutPlan,
} from './types';

type StoredUser = User & { password: string };

type StoredHistory = HistoryEntry & { user_id: number };

const HEURISTICS: Record<Difficulty, { sets: number; reps: string; rest_seconds: number }> = {
  beginner: { sets: 2, reps: '10', rest_seconds: 45 },
  intermediate: { sets: 3, reps: '12', rest_seconds: 40 },
  advanced: { sets: 4, reps: '15', rest_seconds: 30 },
};

type Store = {
  users: StoredUser[];
  nextUserId: number;
  history: StoredHistory[];
  nextHistoryId: number;
};

function isoNow(): string {
  return new Date().toISOString();
}

function seedStore(): Store {
  return {
    users: [
      {
        id: 1,
        email: DEMO_USER.email,
        name: DEMO_USER.name,
        created_at: '2026-01-01T00:00:00.000Z',
        password: DEMO_USER.password,
      },
    ],
    nextUserId: 2,
    history: [],
    nextHistoryId: 1,
  };
}

let store: Store = seedStore();

export function resetMockStore(): void {
  store = seedStore();
}

function encodeToken(userId: number): string {
  return `mock-token-${userId}`;
}

function userIdFromToken(token: string): number {
  if (!token) {
    throw new ApiError(401, 'Not authenticated');
  }
  const match = /^mock-token-(\d+)$/.exec(token);
  if (!match) {
    throw new ApiError(401, 'Invalid token');
  }
  return Number(match[1]);
}

function requireUser(token: string): StoredUser {
  const id = userIdFromToken(token);
  const user = store.users.find((item) => item.id === id);
  if (!user) {
    throw new ApiError(401, 'Invalid token');
  }
  return user;
}

function publicUser(user: StoredUser): User {
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    created_at: user.created_at,
  };
}

function shuffle<T>(items: T[]): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function difficultyRank(value: Difficulty): number {
  return value === 'beginner' ? 0 : value === 'intermediate' ? 1 : 2;
}

function filterExercises(muscleGroups: string[], difficulty: Difficulty): FixtureExercise[] {
  const requested = muscleGroups.map((group) => group.toLowerCase());
  const rank = difficultyRank(difficulty);
  let matches = FIXTURE_EXERCISES.filter((exercise) => difficultyRank(exercise.difficulty) <= rank);
  if (requested.length) {
    const filtered = matches.filter((exercise) => requested.includes(exercise.muscle_group));
    if (filtered.length) {
      matches = filtered;
    }
  }
  return matches.length ? matches : [...FIXTURE_EXERCISES];
}

function exerciseCount(durationMinutes: number): number {
  return Math.max(3, Math.min(8, Math.round(durationMinutes / 5)));
}

function toPlanned(exercise: FixtureExercise, difficulty: Difficulty): PlannedExercise {
  const heuristic = HEURISTICS[difficulty];
  return {
    exercise_id: exercise.id,
    name: exercise.name,
    illustration_slug: exercise.illustration_slug,
    sets: heuristic.sets,
    reps: heuristic.reps,
    rest_seconds: heuristic.rest_seconds,
    notes: exercise.instructions,
  };
}

function buildPlan(options: {
  title: string;
  durationMinutes: number;
  difficulty: Difficulty;
  source: 'random' | 'ai';
  muscleGroups: string[];
}): WorkoutPlan {
  const pool = shuffle(filterExercises(options.muscleGroups, options.difficulty));
  const count = exerciseCount(options.durationMinutes);
  const picked: FixtureExercise[] = [];
  for (let i = 0; i < count; i += 1) {
    picked.push(pool[i % pool.length]);
  }
  return {
    title: options.title,
    duration_minutes: options.durationMinutes,
    difficulty: options.difficulty,
    source: options.source,
    exercises: picked.map((exercise) => toPlanned(exercise, options.difficulty)),
  };
}

function inferMuscleGroups(text: string): string[] {
  const haystack = text.toLowerCase();
  const mapping: Record<string, string[]> = {
    back: ['back', 'row', 'posture'],
    chest: ['chest', 'push', 'press'],
    legs: ['leg', 'squat', 'glute', 'lunge'],
    core: ['core', 'abs', 'plank'],
    shoulders: ['shoulder', 'pull'],
    arms: ['arm', 'bicep', 'tricep', 'curl'],
  };
  return Object.entries(mapping)
    .filter(([, keywords]) => keywords.some((keyword) => haystack.includes(keyword)))
    .map(([group]) => group);
}

function inferDifficulty(text: string): Difficulty {
  const haystack = text.toLowerCase();
  if (haystack.includes('advanced') || haystack.includes('hard')) {
    return 'advanced';
  }
  if (haystack.includes('intermediate') || haystack.includes('moderate')) {
    return 'intermediate';
  }
  return 'beginner';
}

function toPublicHistory(entry: StoredHistory): HistoryEntry {
  return {
    id: entry.id,
    workout_plan: entry.workout_plan,
    completed_at: entry.completed_at,
    notes: entry.notes,
    created_at: entry.created_at,
  };
}

export const mockAdapter: ApiClient = {
  async register(body: RegisterRequest): Promise<User> {
    const email = body.email.trim().toLowerCase();
    if (!email || !body.password) {
      throw new ApiError(400, 'Email and password are required');
    }
    if (store.users.some((user) => user.email === email)) {
      throw new ApiError(400, 'Email already registered');
    }
    const user: StoredUser = {
      id: store.nextUserId,
      email,
      name: body.name?.trim() ? body.name.trim() : null,
      created_at: isoNow(),
      password: body.password,
    };
    store.nextUserId += 1;
    store.users.push(user);
    return publicUser(user);
  },

  async login(body: LoginRequest): Promise<TokenResponse> {
    const email = body.email.trim().toLowerCase();
    const user = store.users.find((item) => item.email === email && item.password === body.password);
    if (!user) {
      throw new ApiError(401, 'Invalid email or password');
    }
    return { access_token: encodeToken(user.id), token_type: 'bearer' };
  },

  async me(token: string): Promise<User> {
    return publicUser(requireUser(token));
  },

  async generateWorkout(token: string, body: GenerateWorkoutRequest): Promise<WorkoutPlan> {
    requireUser(token);
    const groups = body.muscle_groups ?? [];
    const titleGroups = groups.length ? groups.join(' + ') : 'full body';
    return buildPlan({
      title: `Draw-a-Card · ${titleGroups}`,
      durationMinutes: body.duration_minutes,
      difficulty: body.difficulty,
      source: 'random',
      muscleGroups: groups,
    });
  },

  async generateAiWorkout(token: string, body: AiGenerateRequest): Promise<WorkoutPlan> {
    requireUser(token);
    const blob = `${body.goals} ${body.notes ?? ''}`;
    return buildPlan({
      title: body.goals.trim() ? `AI · ${body.goals.trim()}` : 'AI custom workout',
      durationMinutes: body.available_time_minutes,
      difficulty: inferDifficulty(blob),
      source: 'ai',
      muscleGroups: inferMuscleGroups(blob),
    });
  },

  async saveHistory(token: string, body: SaveHistoryRequest): Promise<HistoryEntry> {
    const user = requireUser(token);
    const entry: StoredHistory = {
      id: store.nextHistoryId,
      user_id: user.id,
      workout_plan: body.workout_plan,
      completed_at: body.completed_at,
      notes: body.notes,
      created_at: isoNow(),
    };
    store.nextHistoryId += 1;
    store.history.push(entry);
    return toPublicHistory(entry);
  },

  async listHistory(token: string): Promise<HistoryEntry[]> {
    const user = requireUser(token);
    return store.history
      .filter((entry) => entry.user_id === user.id)
      .sort((a, b) => (a.created_at < b.created_at ? 1 : a.created_at > b.created_at ? -1 : b.id - a.id))
      .map(toPublicHistory);
  },
};
