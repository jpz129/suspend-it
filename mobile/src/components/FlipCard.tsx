import { useState } from "react";
import { Pressable, StyleSheet } from "react-native";
import Animated, {
  interpolate,
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";

import { IllustrationCard } from "../illustrations";
import type { WorkoutExercise } from "../types/api";
import { Text, View } from "react-native";

export function FlipCard({ exercise }: { exercise: WorkoutExercise }) {
  const spin = useSharedValue(0);
  const [flipped, setFlipped] = useState(false);

  const frontStyle = useAnimatedStyle(() => ({
    transform: [{ rotateY: `${interpolate(spin.value, [0, 1], [0, 180])}deg` }],
    backfaceVisibility: "hidden",
  }));
  const backStyle = useAnimatedStyle(() => ({
    transform: [{ rotateY: `${interpolate(spin.value, [0, 1], [180, 360])}deg` }],
    backfaceVisibility: "hidden",
  }));

  const onPress = () => {
    const next = flipped ? 0 : 1;
    spin.value = withTiming(next, { duration: 450 });
    setFlipped(!flipped);
  };

  return (
    <Pressable onPress={onPress} style={styles.wrap}>
      <Animated.View style={[styles.face, frontStyle]}>
        <IllustrationCard slug={exercise.illustration_slug} label={exercise.name} />
        <Text style={styles.hint}>Tap to flip</Text>
      </Animated.View>
      <Animated.View style={[styles.face, styles.back, backStyle]}>
        <Text style={styles.name}>{exercise.name}</Text>
        <Text style={styles.meta}>
          {exercise.sets} sets × {exercise.reps} reps
        </Text>
        <Text style={styles.meta}>Rest {exercise.rest_seconds}s</Text>
        {exercise.notes ? <Text style={styles.notes}>{exercise.notes}</Text> : null}
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: {
    height: 280,
    marginBottom: 16,
  },
  face: {
    ...StyleSheet.absoluteFillObject,
  },
  back: {
    backgroundColor: "#222",
    borderRadius: 20,
    padding: 24,
    justifyContent: "center",
  },
  hint: {
    textAlign: "center",
    marginTop: 8,
    color: "#666",
  },
  name: {
    color: "white",
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 12,
  },
  meta: {
    color: "#ddd",
    fontSize: 18,
    marginBottom: 6,
  },
  notes: {
    color: "#bbb",
    marginTop: 12,
  },
});
