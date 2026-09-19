import { useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

import type { WorkoutPlan } from '../api/types';
import { colors, spacing } from '../theme';
import { Button } from './Button';
import { FlipCard } from './FlipCard';

type Props = {
  plan: WorkoutPlan;
  onStart: () => void;
};

export function PlanReveal({ plan, onStart }: Props) {
  const [flipped, setFlipped] = useState<boolean[]>(() => plan.exercises.map(() => false));

  function flipAt(index: number) {
    setFlipped((current) => current.map((value, i) => (i === index ? true : value)));
  }

  function flipAll() {
    setFlipped(plan.exercises.map(() => true));
  }

  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>{plan.title}</Text>
      <Text style={styles.sub}>
        {plan.duration_minutes} min · {plan.difficulty} · {plan.source}
      </Text>
      <View style={styles.actions}>
        <Button label="Flip all cards" onPress={flipAll} variant="secondary" />
      </View>
      {plan.exercises.map((exercise, index) => (
        <FlipCard
          key={`${exercise.exercise_id}-${index}`}
          exercise={exercise}
          flipped={Boolean(flipped[index])}
          onFlip={() => flipAt(index)}
        />
      ))}
      <Button label="Start workout" onPress={onStart} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    gap: spacing.md,
    paddingBottom: spacing.xl,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: colors.ink,
  },
  sub: {
    color: colors.muted,
    textTransform: 'capitalize',
    marginTop: -8,
  },
  actions: {
    alignSelf: 'flex-start',
  },
});
