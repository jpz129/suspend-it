import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'suspend_it_access_token';

const memory = new Map<string, string>();

function webStore(): Storage | null {
  try {
    return globalThis.localStorage ?? null;
  } catch {
    return null;
  }
}

export async function getStoredToken(): Promise<string | null> {
  if (Platform.OS === 'web') {
    return webStore()?.getItem(TOKEN_KEY) ?? memory.get(TOKEN_KEY) ?? null;
  }
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function setStoredToken(token: string): Promise<void> {
  if (Platform.OS === 'web') {
    webStore()?.setItem(TOKEN_KEY, token);
    memory.set(TOKEN_KEY, token);
    return;
  }
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function clearStoredToken(): Promise<void> {
  if (Platform.OS === 'web') {
    webStore()?.removeItem(TOKEN_KEY);
    memory.delete(TOKEN_KEY);
    return;
  }
  await SecureStore.deleteItemAsync(TOKEN_KEY);
}
