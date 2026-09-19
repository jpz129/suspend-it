import { useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { api, errorMessage } from '../api/client';
import { useRequiredToken } from '../auth/AuthContext';
import { Button } from '../components/Button';
import { ErrorBanner } from '../components/ErrorBanner';
import { ExerciseCard } from '../components/ExerciseCard';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, radius, spacing } from '../theme';
import type { RootStackScreenProps } from '../navigation/types';

export function WorkoutPlayerScreen({ navigation, route }: RootStackScreenProps<'WorkoutPlayer'>) {
  const { plan } = route.params;
  const token = useRequiredToken();
  const queryClient = useQueryClient();
  const [done, setDone] = useState<boolean[]>(() => plan.exercises.map(() => false));
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const remaining = done.filter((value) => !value).length;
  const allDone = remaining === 0;

  function toggle(index: number) {
    setDone((current) => current.map((value, i) => (i === index ? !value : value)));
  }

  async function finish() {
    setError(null);
    setLoading(true);
    try {
      await api.saveHistory(token, {
        workout_plan: plan,
        completed_at: new Date().toISOString(),
        notes: notes.trim() ? notes.trim() : null,
      });
      await queryClient.invalidateQueries({ queryKey: ['history'] });
      navigation.navigate('Main', { screen: 'History' });
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen>
      <Text style={styles.title}>{plan.title}</Text>
      <Text style={styles.sub}>
        {allDone ? 'All exercises checked.' : `${remaining} remaining`}
      </Text>
      <ErrorBanner message={error} />
      {plan.exercises.map((exercise, index) => {
        const checked = Boolean(done[index]);
        return (
          <Pressable
            key={`${exercise.exercise_id}-${index}`}
            onPress={() => toggle(index)}
            style={[styles.row, checked && styles.rowDone]}
            accessibilityRole="checkbox"
            accessibilityState={{ checked }}
          >
            <View style={[styles.box, checked && styles.boxOn]}>
              <Text style={styles.check}>{checked ? '✓' : ''}</Text>
            </View>
            <View style={styles.card}>
              <ExerciseCard exercise={exercise} compact />
            </View>
          </Pressable>
        );
      })}
      <TextField
        label="Notes (optional)"
        value={notes}
        onChangeText={setNotes}
        autoCapitalize="sentences"
        multiline
        placeholder="How did it feel?"
      />
      <Button
        label="Finish and save"
        onPress={() => void finish()}
        loading={loading}
        disabled={!allDone}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.ink,
  },
  sub: {
    color: colors.muted,
    marginTop: -8,
  },
  row: {
    flexDirection: 'row',
    gap: spacing.sm,
    alignItems: 'center',
  },
  rowDone: {
    opacity: 0.55,
  },
  box: {
    width: 28,
    height: 28,
    borderRadius: radius.sm,
    borderWidth: 2,
    borderColor: colors.accent,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
  },
  boxOn: {
    backgroundColor: colors.accent,
  },
  check: {
    color: colors.accentText,
    fontWeight: '700',
  },
  card: {
    flex: 1,
  },
});
