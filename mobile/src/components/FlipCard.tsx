import { useEffect } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import Animated, {
  Easing,
  interpolate,
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from 'react-native-reanimated';

import type { PlannedExercise } from '../api/types';
import { colors, radius } from '../theme';
import { ExerciseCard } from './ExerciseCard';

type Props = {
  exercise: PlannedExercise;
  flipped: boolean;
  onFlip: () => void;
};

export function FlipCard({ exercise, flipped, onFlip }: Props) {
  const progress = useSharedValue(flipped ? 1 : 0);

  useEffect(() => {
    progress.value = withTiming(flipped ? 1 : 0, {
      duration: 520,
      easing: Easing.inOut(Easing.cubic),
    });
  }, [flipped, progress]);

  const frontStyle = useAnimatedStyle(() => ({
    transform: [
      { perspective: 1200 },
      { rotateY: `${interpolate(progress.value, [0, 1], [0, 180])}deg` },
    ],
    backfaceVisibility: 'hidden' as const,
  }));

  const backStyle = useAnimatedStyle(() => ({
    transform: [
      { perspective: 1200 },
      { rotateY: `${interpolate(progress.value, [0, 1], [180, 360])}deg` },
    ],
    backfaceVisibility: 'hidden' as const,
  }));

  return (
    <Pressable onPress={onFlip} style={styles.wrap} accessibilityRole="button">
      <View style={styles.scene}>
        <Animated.View style={[styles.face, frontStyle]}>
          <View style={styles.back}>
            <Text style={styles.backKicker}>SUSPEND IT</Text>
            <Text style={styles.backTitle}>Draw a card</Text>
            <Text style={styles.backHint}>Tap to reveal</Text>
          </View>
        </Animated.View>
        <Animated.View style={[styles.face, styles.faceBack, backStyle]}>
          <ExerciseCard exercise={exercise} />
        </Animated.View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: {
    width: '100%',
  },
  scene: {
    minHeight: 390,
  },
  face: {
    ...StyleSheet.absoluteFill,
  },
  faceBack: {
    // stacked on top; hidden via backface until flipped
  },
  back: {
    flex: 1,
    backgroundColor: colors.cardBack,
    borderRadius: radius.lg,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    minHeight: 390,
    borderWidth: 1,
    borderColor: '#22312B',
  },
  backKicker: {
    color: '#C5D2CB',
    letterSpacing: 3,
    fontSize: 12,
    fontWeight: '700',
  },
  backTitle: {
    color: colors.accentText,
    fontSize: 28,
    fontWeight: '700',
  },
  backHint: {
    color: '#C5D2CB',
    marginTop: 8,
  },
});
