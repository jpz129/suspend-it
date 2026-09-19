import { StyleSheet, Text } from 'react-native';

import { API_URL, USE_MOCKS } from '../api/client';
import { useAuth } from '../auth/AuthContext';
import { Button } from '../components/Button';
import { Screen } from '../components/Screen';
import { colors, spacing } from '../theme';
import type { TabScreenProps } from '../navigation/types';

export function SettingsScreen(_props: TabScreenProps<'Settings'>) {
  const { user, logout } = useAuth();

  return (
    <Screen>
      <Text style={styles.title}>Settings</Text>
      <Text style={styles.label}>Signed in</Text>
      <Text style={styles.value}>{user?.name ?? '—'}</Text>
      <Text style={styles.value}>{user?.email}</Text>

      <Text style={styles.label}>API</Text>
      <Text style={styles.value}>{USE_MOCKS ? 'Mock fixtures (offline demo)' : API_URL}</Text>

      <Text style={styles.label}>About</Text>
      <Text style={styles.body}>
        Suspend It is a TRX / suspension-trainer workout app. Illustrated cards are placeholders
        and can be swapped without code changes.
      </Text>
      <Text style={styles.attribution}>Exercise data from wger.de</Text>
      <Text style={styles.legal}>wger exercise data is licensed CC-BY-SA.</Text>

      <Button label="Log out" variant="secondary" onPress={() => void logout()} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.ink,
  },
  label: {
    marginTop: spacing.sm,
    fontWeight: '700',
    color: colors.ink,
  },
  value: {
    color: colors.ink,
    fontSize: 16,
  },
  body: {
    color: colors.muted,
    lineHeight: 20,
  },
  attribution: {
    color: colors.ink,
    fontWeight: '700',
    marginTop: spacing.sm,
  },
  legal: {
    color: colors.muted,
    fontSize: 13,
    marginBottom: spacing.md,
  },
});
