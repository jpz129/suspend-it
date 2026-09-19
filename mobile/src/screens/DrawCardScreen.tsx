import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { api, errorMessage, type Difficulty, type WorkoutPlan } from '../api/client';
import { useRequiredToken } from '../auth/AuthContext';
import { Button } from '../components/Button';
import { Chip } from '../components/Chip';
import { ErrorBanner } from '../components/ErrorBanner';
import { PlanReveal } from '../components/PlanReveal';
import { Screen } from '../components/Screen';
import { colors, spacing } from '../theme';
import type { RootStackScreenProps } from '../navigation/types';

const DURATIONS = [15, 20, 30, 45];
const GROUPS = ['back', 'chest', 'legs', 'core', 'shoulders', 'arms'];
const DIFFICULTIES: Difficulty[] = ['beginner', 'intermediate', 'advanced'];

export function DrawCardScreen({ navigation }: RootStackScreenProps<'DrawCard'>) {
  const token = useRequiredToken();
  const [duration, setDuration] = useState(30);
  const [groups, setGroups] = useState<string[]>(['back', 'legs']);
  const [difficulty, setDifficulty] = useState<Difficulty>('beginner');
  const [plan, setPlan] = useState<WorkoutPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function toggleGroup(group: string) {
    setGroups((current) =>
      current.includes(group) ? current.filter((item) => item !== group) : [...current, group],
    );
  }

  async function generate() {
    setError(null);
    setLoading(true);
    try {
      const result = await api.generateWorkout(token, {
        duration_minutes: duration,
        muscle_groups: groups,
        difficulty,
      });
      setPlan(result);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <Screen>
      <Text style={styles.title}>Draw a card</Text>
      <ErrorBanner message={error} />

      {!plan ? (
        <>
          <Text style={styles.label}>Duration</Text>
          <View style={styles.row}>
            {DURATIONS.map((item) => (
              <Chip
                key={item}
                label={`${item} min`}
                selected={duration === item}
                onPress={() => setDuration(item)}
              />
            ))}
          </View>
          <Text style={styles.label}>Muscle groups</Text>
          <View style={styles.row}>
            {GROUPS.map((item) => (
              <Chip
                key={item}
                label={item}
                selected={groups.includes(item)}
                onPress={() => toggleGroup(item)}
              />
            ))}
          </View>
          <Text style={styles.label}>Difficulty</Text>
          <View style={styles.row}>
            {DIFFICULTIES.map((item) => (
              <Chip
                key={item}
                label={item}
                selected={difficulty === item}
                onPress={() => setDifficulty(item)}
              />
            ))}
          </View>
          <Button label="Generate workout" onPress={() => void generate()} loading={loading} />
        </>
      ) : (
        <>
          <PlanReveal
            plan={plan}
            onStart={() => navigation.navigate('WorkoutPlayer', { plan })}
          />
          <Button label="Draw again" variant="ghost" onPress={() => setPlan(null)} />
        </>
      )}
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
    fontWeight: '700',
    color: colors.ink,
    marginTop: spacing.sm,
  },
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
});
