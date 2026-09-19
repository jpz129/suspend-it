import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { api, errorMessage, type WorkoutPlan } from '../api/client';
import { useRequiredToken } from '../auth/AuthContext';
import { Button } from '../components/Button';
import { Chip } from '../components/Chip';
import { ErrorBanner } from '../components/ErrorBanner';
import { PlanReveal } from '../components/PlanReveal';
import { Screen } from '../components/Screen';
import { TextField } from '../components/TextField';
import { colors, spacing } from '../theme';
import type { RootStackScreenProps } from '../navigation/types';

const TIMES = [15, 20, 30, 45];
const EQUIPMENT = ['TRX', 'bodyweight', 'bands'];

export function AiWorkoutScreen({ navigation }: RootStackScreenProps<'AiWorkout'>) {
  const token = useRequiredToken();
  const [goals, setGoals] = useState('Build a stronger back and core');
  const [minutes, setMinutes] = useState(20);
  const [equipment, setEquipment] = useState<string[]>(['TRX']);
  const [notes, setNotes] = useState('');
  const [plan, setPlan] = useState<WorkoutPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function toggleEquipment(item: string) {
    setEquipment((current) =>
      current.includes(item) ? current.filter((value) => value !== item) : [...current, item],
    );
  }

  async function generate() {
    setError(null);
    setLoading(true);
    try {
      const result = await api.generateAiWorkout(token, {
        goals,
        available_time_minutes: minutes,
        equipment,
        notes: notes.trim() ? notes.trim() : null,
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
      <Text style={styles.title}>AI workout</Text>
      <ErrorBanner message={error} />

      {!plan ? (
        <>
          <TextField
            label="Goals"
            value={goals}
            onChangeText={setGoals}
            autoCapitalize="sentences"
            multiline
            placeholder="What do you want to work on?"
          />
          <Text style={styles.label}>Available time</Text>
          <View style={styles.row}>
            {TIMES.map((item) => (
              <Chip
                key={item}
                label={`${item} min`}
                selected={minutes === item}
                onPress={() => setMinutes(item)}
              />
            ))}
          </View>
          <Text style={styles.label}>Equipment</Text>
          <View style={styles.row}>
            {EQUIPMENT.map((item) => (
              <Chip
                key={item}
                label={item}
                selected={equipment.includes(item)}
                onPress={() => toggleEquipment(item)}
              />
            ))}
          </View>
          <TextField
            label="Notes (optional)"
            value={notes}
            onChangeText={setNotes}
            autoCapitalize="sentences"
            multiline
            placeholder="Injuries, preferences…"
          />
          <Button label="Generate with AI" onPress={() => void generate()} loading={loading} />
        </>
      ) : (
        <>
          <PlanReveal
            plan={plan}
            onStart={() => navigation.navigate('WorkoutPlayer', { plan })}
          />
          <Button label="Try another prompt" variant="ghost" onPress={() => setPlan(null)} />
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
