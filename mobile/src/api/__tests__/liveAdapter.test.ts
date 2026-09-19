import { extractDetail } from '../errors';
import { liveAdapter } from '../liveAdapter';

describe('liveAdapter', () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  it('sends Bearer auth and JSON bodies to the contract paths', async () => {
    const fetchMock = jest.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith('/auth/login')) {
        return new Response(JSON.stringify({ access_token: 'tok', token_type: 'bearer' }), {
          status: 200,
        });
      }
      if (url.endsWith('/auth/me')) {
        return new Response(
          JSON.stringify({
            id: 1,
            email: 'a@b.c',
            name: null,
            created_at: '2026-01-01T00:00:00Z',
          }),
          { status: 200 },
        );
      }
      return new Response(JSON.stringify({ detail: 'missing mock' }), { status: 404 });
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    const token = await liveAdapter.login({ email: 'a@b.c', password: 'x' });
    expect(token).toEqual({ access_token: 'tok', token_type: 'bearer' });

    const me = await liveAdapter.me('tok');
    expect(me.email).toBe('a@b.c');

    const loginCall = fetchMock.mock.calls[0];
    expect(String(loginCall[0])).toMatch(/\/auth\/login$/);
    expect(loginCall[1]?.method).toBe('POST');
    expect(JSON.parse(String(loginCall[1]?.body))).toEqual({ email: 'a@b.c', password: 'x' });

    const meHeaders = new Headers(fetchMock.mock.calls[1][1]?.headers);
    expect(meHeaders.get('Authorization')).toBe('Bearer tok');
  });

  it('surfaces FastAPI detail on error', async () => {
    global.fetch = jest.fn(async () =>
      new Response(JSON.stringify({ detail: 'Not authenticated' }), { status: 401 }),
    ) as unknown as typeof fetch;

    await expect(liveAdapter.me('bad')).rejects.toMatchObject({
      status: 401,
      detail: 'Not authenticated',
    });
    expect(extractDetail({ detail: 'Not authenticated' })).toBe('Not authenticated');
  });
});
