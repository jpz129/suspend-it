import { API_URL } from './config';
import { ApiError, extractDetail } from './errors';
import type { ApiClient } from './types';

async function request<T>(
  path: string,
  options: {
    method?: string;
    body?: unknown;
    token?: string;
  } = {},
): Promise<T> {
  const headers: Record<string, string> = {
    Accept: 'application/json',
  };
  if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (options.token) {
    headers.Authorization = `Bearer ${options.token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      method: options.method ?? 'GET',
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });
  } catch {
    throw new ApiError(0, `Could not reach API at ${API_URL}`);
  }

  const text = await response.text();
  let payload: unknown = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = { detail: text };
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, extractDetail(payload, `Request failed (${response.status})`));
  }

  return payload as T;
}

export const liveAdapter: ApiClient = {
  register: (body) => request('/auth/register', { method: 'POST', body }),
  login: (body) => request('/auth/login', { method: 'POST', body }),
  me: (token) => request('/auth/me', { token }),
  generateWorkout: (token, body) =>
    request('/workouts/generate', { method: 'POST', token, body }),
  generateAiWorkout: (token, body) =>
    request('/workouts/ai-generate', { method: 'POST', token, body }),
  saveHistory: (token, body) => request('/history', { method: 'POST', token, body }),
  listHistory: (token) => request('/history', { token }),
};
