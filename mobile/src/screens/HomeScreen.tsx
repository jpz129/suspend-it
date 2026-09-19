import { Pressable, StyleSheet, Text } from 'react-native';

import { useAuth } from '../auth/AuthContext';
import { Screen } from '../components/Screen';
import { colors, radius, spacing } from '../theme';
import type { TabScreenProps } from '../navigation/types';

export function HomeScreen({ navigation }: TabScreenProps<'Home'>) {
  const { user } = useAuth();
  const first = user?.name?.split(' ')[0] ?? 'there';

  return (
    <Screen>
      <Text style={styles.hello}>Hi {first}</Text>
      <Text style={styles.lede}>Pick a workout. Same cards either way.</Text>

      <Pressable
        style={styles.tile}
        onPress={() => navigation.navigate('DrawCard')}
        accessibilityRole="button"
      >
        <Text style={styles.tileKicker}>RANDOM</Text>
        <Text style={styles.tileTitle}>Draw a card</Text>
        <Text style={styles.tileBody}>Filter by time, muscle group, and difficulty.</Text>
      </Pressable>

      <Pressable
        style={styles.tile}
        onPress={() => navigation.navigate('AiWorkout')}
        accessibilityRole="button"
      >
        <Text style={styles.tileKicker}>AI</Text>
        <Text style={styles.tileTitle}>AI workout</Text>
        <Text style={styles.tileBody}>Describe a goal and available time.</Text>
      </Pressable>

      <Text style={styles.foot}>Past sessions live in the History tab.</Text>
    </Screen>
  );
}

const styles = StyleSheet.create({
  hello: {
    fontSize: 28,
    fontWeight: '700',
    color: colors.ink,
  },
  lede: {
    color: colors.muted,
    fontSize: 16,
    marginBottom: spacing.sm,
  },
  tile: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.line,
    gap: 6,
  },
  tileKicker: {
    color: colors.accent,
    fontWeight: '700',
    letterSpacing: 1.5,
    fontSize: 12,
  },
  tileTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: colors.ink,
  },
  tileBody: {
    color: colors.muted,
    fontSize: 15,
  },
  foot: {
    color: colors.muted,
    marginTop: spacing.sm,
  },
});
