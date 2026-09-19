import * as SecureStore from "expo-secure-store";

import { mockHistory, mockPlan, mockUser } from "./mocks";
import type {
  HistoryEntry,
  TokenResponse,
  User,
  WorkoutPlan,
} from "../types/api";

const TOKEN_KEY = "suspend_it_jwt";

export const USE_MOCKS =
  (process.env.EXPO_PUBLIC_USE_MOCKS ?? "true") !== "false";

export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

type AuthedOptions = RequestInit & { token?: string | null };

async function request<T>(path: string, options: AuthedOptions = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const detail = data?.detail ?? res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data as T;
}

let memoryHistory = [...mockHistory];
let nextHistoryId = 2;

export async function saveToken(token: string): Promise<void> {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function loadToken(): Promise<string | null> {
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function clearToken(): Promise<void> {
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}

export const api = {
  async register(email: string, password: string, name: string | null): Promise<User> {
    if (USE_MOCKS) {
      return { ...mockUser, email, name };
    }
    return request<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, name }),
    });
  },

  async login(email: string, password: string): Promise<TokenResponse> {
    if (USE_MOCKS) {
      return { access_token: "mock-token", token_type: "bearer" };
    }
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  async me(token: string): Promise<User> {
    if (USE_MOCKS) {
      return mockUser;
    }
    return request<User>("/auth/me", { token });
  },

  async generateWorkout(
    token: string,
    body: { duration_minutes: number; muscle_groups: string[]; difficulty: string },
  ): Promise<WorkoutPlan> {
    if (USE_MOCKS) {
      return mockPlan("random", `${body.difficulty} draw`);
    }
    return request<WorkoutPlan>("/workouts/generate", {
      method: "POST",
      token,
      body: JSON.stringify(body),
    });
  },

  async generateAiWorkout(
    token: string,
    body: {
      goals: string;
      available_time_minutes: number;
      equipment: string[];
      notes: string | null;
    },
  ): Promise<WorkoutPlan> {
    if (USE_MOCKS) {
      return mockPlan("ai", body.goals || "AI workout");
    }
    return request<WorkoutPlan>("/workouts/ai-generate", {
      method: "POST",
      token,
      body: JSON.stringify(body),
    });
  },

  async saveHistory(
    token: string,
    body: { workout_plan: WorkoutPlan; completed_at: string; notes: string | null },
  ): Promise<HistoryEntry> {
    if (USE_MOCKS) {
      const entry: HistoryEntry = {
        id: nextHistoryId++,
        workout_plan: body.workout_plan,
        completed_at: body.completed_at,
        notes: body.notes,
        created_at: body.completed_at,
      };
      memoryHistory = [entry, ...memoryHistory];
      return entry;
    }
    return request<HistoryEntry>("/history", {
      method: "POST",
      token,
      body: JSON.stringify(body),
    });
  },

  async listHistory(token: string): Promise<HistoryEntry[]> {
    if (USE_MOCKS) {
      return memoryHistory;
    }
    return request<HistoryEntry[]>("/history", { token });
  },
};
