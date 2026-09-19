type Extra = {
  apiUrl?: string;
  useMocks?: boolean | string;
};

function readExtra(): Extra {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const Constants = require('expo-constants').default as {
      expoConfig?: { extra?: Extra };
    };
    return Constants?.expoConfig?.extra ?? {};
  } catch {
    return {};
  }
}

function parseBool(value: unknown, fallback: boolean): boolean {
  if (value === undefined || value === null || value === '') {
    return fallback;
  }
  if (typeof value === 'boolean') {
    return value;
  }
  const normalized = String(value).toLowerCase();
  if (normalized === 'true' || normalized === '1') {
    return true;
  }
  if (normalized === 'false' || normalized === '0') {
    return false;
  }
  return fallback;
}

const extra = readExtra();

/** Default true so Expo Go can demo without a running backend. */
export const USE_MOCKS = parseBool(
  process.env.EXPO_PUBLIC_USE_MOCKS ?? extra.useMocks,
  true,
);

export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? extra.apiUrl ?? 'http://localhost:8000';
