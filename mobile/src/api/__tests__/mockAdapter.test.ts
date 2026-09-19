import { extractDetail, ApiError } from '../errors';
import { FIXTURE_EXERCISES } from '../fixtures';
import { mockAdapter, resetMockStore } from '../mockAdapter';
import { ILLUSTRATION_SLUGS } from '../../illustrations/slugs';
import type { WorkoutPlan } from '../types';

const DEMO = { email: 'demo@suspend.it', password: 'password123' };

beforeEach(() => {
  resetMockStore();
});

describe('mockAdapter auth', () => {
  it('registers, logs in, and returns the user from /me', async () => {
    const created = await mockAdapter.register({
      email: 'new@example.com',
      password: 'secret',
      name: 'Ada',
    });
    expect(created.id).toBeGreaterThan(0);
    expect(created.email).toBe('new@example.com');
    expect(created.name).toBe('Ada');
    expect(created.created_at).toMatch(/Z$/);

    const token = await mockAdapter.login({
      email: 'new@example.com',
      password: 'secret',
    });
    expect(token.token_type).toBe('bearer');
    expect(token.access_token).toBeTruthy();

    const me = await mockAdapter.me(token.access_token);
    expect(me.email).toBe('new@example.com');
    expect(me.name).toBe('Ada');
  });

  it('rejects duplicate registration and bad credentials', async () => {
    await expect(
      mockAdapter.register({ email: DEMO.email, password: 'x', name: null }),
    ).rejects.toMatchObject({ status: 400, detail: 'Email already registered' } satisfies Partial<ApiError>);

    await expect(
      mockAdapter.login({ email: DEMO.email, password: 'wrong' }),
    ).rejects.toMatchObject({ status: 401 });
  });

  it('returns 401 for missing/invalid tokens', async () => {
    await expect(mockAdapter.me('')).rejects.toMatchObject({ status: 401 });
    await expect(mockAdapter.me('not-a-token')).rejects.toMatchObject({ status: 401 });
  });
});

describe('mockAdapter workouts', () => {
  async function authToken() {
    const { access_token } = await mockAdapter.login(DEMO);
    return access_token;
  }

  function assertPlan(plan: WorkoutPlan, source: 'random' | 'ai') {
    expect(plan.title).toBeTruthy();
    expect(plan.duration_minutes).toBeGreaterThan(0);
    expect(['beginner', 'intermediate', 'advanced']).toContain(plan.difficulty);
    expect(plan.source).toBe(source);
    expect(plan.exercises.length).toBeGreaterThan(0);
    for (const exercise of plan.exercises) {
      expect(typeof exercise.exercise_id).toBe('number');
      expect(exercise.name).toBeTruthy();
      expect(exercise.illustration_slug).toBeTruthy();
      expect(typeof exercise.sets).toBe('number');
      expect(typeof exercise.reps).toBe('string');
      expect(typeof exercise.rest_seconds).toBe('number');
    }
  }

  it('generates a random WorkoutPlan for typical filters', async () => {
    const token = await authToken();
    const plan = await mockAdapter.generateWorkout(token, {
      duration_minutes: 30,
      muscle_groups: ['back', 'legs'],
      difficulty: 'beginner',
    });
    assertPlan(plan, 'random');
    expect(plan.duration_minutes).toBe(30);
  });

  it('still returns a plan when filters match few exercises', async () => {
    const token = await authToken();
    const plan = await mockAdapter.generateWorkout(token, {
      duration_minutes: 15,
      muscle_groups: ['shoulders'],
      difficulty: 'beginner',
    });
    assertPlan(plan, 'random');
    expect(plan.exercises.length).toBeGreaterThanOrEqual(3);
  });

  it('generates an AI WorkoutPlan with the same shape', async () => {
    const token = await authToken();
    const plan = await mockAdapter.generateAiWorkout(token, {
      goals: 'stronger back and core',
      available_time_minutes: 20,
      equipment: ['TRX'],
      notes: 'keep it beginner friendly',
    });
    assertPlan(plan, 'ai');
    expect(plan.duration_minutes).toBe(20);
  });
});

describe('mockAdapter history', () => {
  const samplePlan: WorkoutPlan = {
    title: 'Test plan',
    duration_minutes: 20,
    difficulty: 'beginner',
    source: 'random',
    exercises: [
      {
        exercise_id: 1,
        name: 'TRX Row',
        illustration_slug: 'row',
        sets: 2,
        reps: '10',
        rest_seconds: 45,
        notes: null,
      },
    ],
  };

  it('round-trips POST then GET, newest first, scoped to the user', async () => {
    const a = await mockAdapter.login(DEMO);
    const created = await mockAdapter.register({
      email: 'other@example.com',
      password: 'secret',
      name: null,
    });
    expect(created.email).toBe('other@example.com');
    const b = await mockAdapter.login({ email: 'other@example.com', password: 'secret' });

    const first = await mockAdapter.saveHistory(a.access_token, {
      workout_plan: samplePlan,
      completed_at: '2026-01-02T10:00:00.000Z',
      notes: 'first',
    });
    const second = await mockAdapter.saveHistory(a.access_token, {
      workout_plan: { ...samplePlan, title: 'Later plan' },
      completed_at: '2026-01-03T10:00:00.000Z',
      notes: null,
    });
    await mockAdapter.saveHistory(b.access_token, {
      workout_plan: { ...samplePlan, title: 'Other user' },
      completed_at: '2026-01-04T10:00:00.000Z',
      notes: null,
    });

    const list = await mockAdapter.listHistory(a.access_token);
    expect(list.map((entry) => entry.id)).toEqual([second.id, first.id]);
    expect(list[0]?.workout_plan.title).toBe('Later plan');
    expect(list.every((entry) => entry.workout_plan.title !== 'Other user')).toBe(true);

    const other = await mockAdapter.listHistory(b.access_token);
    expect(other).toHaveLength(1);
    expect(other[0]?.workout_plan.title).toBe('Other user');
  });
});

describe('error parsing', () => {
  it('reads FastAPI { detail: string }', () => {
    expect(extractDetail({ detail: 'Not authenticated' })).toBe('Not authenticated');
  });

  it('joins validation error arrays', () => {
    expect(extractDetail({ detail: [{ msg: 'field required' }, { msg: 'invalid' }] })).toBe(
      'field required; invalid',
    );
  });
});

describe('fixtures', () => {
  it('maps every exercise to a known illustration slug', () => {
    const allowed = new Set<string>(ILLUSTRATION_SLUGS);
    for (const exercise of FIXTURE_EXERCISES) {
      expect(allowed.has(exercise.illustration_slug)).toBe(true);
    }
  });
});
