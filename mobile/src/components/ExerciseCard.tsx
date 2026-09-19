import { Image, StyleSheet, Text, View } from 'react-native';

import type { PlannedExercise } from '../api/types';
import { getIllustration } from '../illustrations';
import { colors, radius, spacing } from '../theme';

type Props = {
  exercise: PlannedExercise;
  compact?: boolean;
};

export function ExerciseCard({ exercise, compact }: Props) {
  return (
    <View style={[styles.card, compact && styles.compact]}>
      <Image
        source={getIllustration(exercise.illustration_slug)}
        style={[styles.art, compact && styles.artCompact]}
        resizeMode="cover"
        accessibilityLabel={`${exercise.name} illustration`}
      />
      <View style={styles.meta}>
        <Text style={styles.name}>{exercise.name}</Text>
        <Text style={styles.stats}>
          {exercise.sets} sets · {exercise.reps} reps · {exercise.rest_seconds}s rest
        </Text>
        {exercise.notes ? <Text style={styles.notes}>{exercise.notes}</Text> : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: colors.line,
  },
  compact: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  art: {
    width: '100%',
    height: 280,
    backgroundColor: colors.accent,
  },
  artCompact: {
    width: 88,
    height: 112,
  },
  meta: {
    padding: spacing.md,
    gap: 4,
    flex: 1,
  },
  name: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.ink,
  },
  stats: {
    color: colors.muted,
    fontSize: 15,
  },
  notes: {
    color: colors.ink,
    fontSize: 14,
    marginTop: 4,
  },
});
