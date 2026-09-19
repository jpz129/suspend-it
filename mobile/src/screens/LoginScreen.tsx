import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { USE_MOCKS } from '../api/client';
import { errorMessage } from '../api/errors';
import { DEMO_USER } from '../api/fixtures';
import { useAuth } from '../auth/AuthContext';
import { Button } from '../components/Button';
import { ErrorBanner } from '../components/ErrorBanner';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, spacing } from '../theme';
import type { AuthScreenProps } from '../navigation/types';

export function LoginScreen({ navigation }: AuthScreenProps<'Login'>) {
  const { login } = useAuth();
  const [email, setEmail] = useState(USE_MOCKS ? DEMO_USER.email : '');
  const [password, setPassword] = useState(USE_MOCKS ? DEMO_USER.password : '');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit() {
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen>
      <View style={styles.hero}>
        <Text style={styles.kicker}>SUSPEND IT</Text>
        <Text style={styles.title}>TRX workouts, one card at a time.</Text>
      </View>
      <ErrorBanner message={error} />
      <TextField
        label="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        placeholder="you@example.com"
      />
      <TextField
        label="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        placeholder="••••••••"
      />
      <Button label="Log in" onPress={() => void onSubmit()} loading={loading} />
      <Button
        label="Create an account"
        variant="ghost"
        onPress={() => navigation.navigate('Register')}
      />
      {USE_MOCKS ? (
        <Text style={styles.hint}>
          Mock mode is on. Demo login is prefilled ({DEMO_USER.email}). Registering a new account
          also works locally.
        </Text>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  hero: {
    gap: spacing.sm,
    marginBottom: spacing.sm,
  },
  kicker: {
    letterSpacing: 2,
    fontWeight: '700',
    color: colors.accent,
    fontSize: 13,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.ink,
  },
  hint: {
    color: colors.muted,
    fontSize: 13,
    lineHeight: 18,
  },
});
