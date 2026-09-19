import { useQuery } from '@tanstack/react-query';
import { ActivityIndicator, StyleSheet, Text, View } from 'react-native';

import { api, errorMessage, type HistoryEntry } from '../api/client';
import { useRequiredToken } from '../auth/AuthContext';
import { ErrorBanner } from '../components/ErrorBanner';
import { Screen } from '../components/Screen';
import { colors, radius, spacing } from '../theme';
import type { TabScreenProps } from '../navigation/types';

function formatWhen(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}

function HistoryCard({ entry }: { entry: HistoryEntry }) {
  const plan = entry.workout_plan;
  return (
    <View style={styles.card}>
      <Text style={styles.kicker}>
        {plan.source} · {plan.difficulty}
      </Text>
      <Text style={styles.title}>{plan.title}</Text>
      <Text style={styles.meta}>
        {formatWhen(entry.completed_at)} · {plan.duration_minutes} min · {plan.exercises.length}{' '}
        exercises
      </Text>
      {entry.notes ? <Text style={styles.notes}>{entry.notes}</Text> : null}
    </View>
  );
}

export function HistoryScreen(_props: TabScreenProps<'History'>) {
  const token = useRequiredToken();
  const query = useQuery({
    queryKey: ['history', token],
    queryFn: () => api.listHistory(token),
  });

  return (
    <Screen>
      <Text style={styles.pageTitle}>History</Text>
      {query.isLoading ? <ActivityIndicator color={colors.accent} /> : null}
      <ErrorBanner message={query.error ? errorMessage(query.error) : null} />
      {query.data?.length === 0 ? (
        <Text style={styles.empty}>No completed workouts yet. Finish one to see it here.</Text>
      ) : null}
      {query.data?.map((entry) => (
        <HistoryCard key={entry.id} entry={entry} />
      ))}
    </Screen>
  );
}

const styles = StyleSheet.create({
  pageTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.ink,
  },
  empty: {
    color: colors.muted,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    padding: spacing.md,
    borderWidth: 1,
    borderColor: colors.line,
    gap: 4,
  },
  kicker: {
    color: colors.accent,
    fontWeight: '700',
    fontSize: 12,
    letterSpacing: 1,
    textTransform: 'uppercase',
  },
  title: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.ink,
  },
  meta: {
    color: colors.muted,
    fontSize: 13,
  },
  notes: {
    color: colors.ink,
    marginTop: 4,
  },
});
