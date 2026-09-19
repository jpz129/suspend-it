import { USE_MOCKS } from './config';
import { liveAdapter } from './liveAdapter';
import { mockAdapter } from './mockAdapter';
import type { ApiClient } from './types';

export const api: ApiClient = USE_MOCKS ? mockAdapter : liveAdapter;

export { API_URL, USE_MOCKS } from './config';
export { ApiError, errorMessage } from './errors';
export type {
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
