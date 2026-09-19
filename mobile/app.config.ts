import type { ExpoConfig } from 'expo/config';

const useMocks = process.env.EXPO_PUBLIC_USE_MOCKS !== 'false';
const apiUrl = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

const config: ExpoConfig = {
  name: 'Suspend It',
  slug: 'suspend-it',
  version: '1.0.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  userInterfaceStyle: 'light',
  scheme: 'suspend-it',
  ios: {
    supportsTablet: true,
    bundleIdentifier: 'com.suspendit.app',
  },
  android: {
    adaptiveIcon: {
      backgroundColor: '#3D5A4C',
      foregroundImage: './assets/android-icon-foreground.png',
      backgroundImage: './assets/android-icon-background.png',
      monochromeImage: './assets/android-icon-monochrome.png',
    },
    predictiveBackGestureEnabled: false,
    package: 'com.suspendit.app',
  },
  web: {
    favicon: './assets/favicon.png',
  },
  plugins: ['expo-secure-store'],
  extra: {
    apiUrl,
    useMocks,
  },
};

export default config;
