import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { FlipCard } from "../components/FlipCard";
import type { Difficulty } from "../types/api";

const MUSCLES = ["back", "chest", "legs", "shoulders", "arms", "core"];
const DIFFICULTIES: Difficulty[] = ["beginner", "intermediate", "advanced"];
const DURATIONS = [20, 30, 45];

export function DrawCardScreen({ navigation }: { navigation: any }) {
  const { token } = useAuth();
  const [duration, setDuration] = useState(30);
  const [difficulty, setDifficulty] = useState<Difficulty>("beginner");
  const [muscles, setMuscles] = useState<string[]>(["back"]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggle = (m: string) => {
    setMuscles((curr) => (curr.includes(m) ? curr.filter((x) => x !== m) : [...curr, m]));
  };

  const draw = async () => {
    if (!token) return;
    setBusy(true);
    setError(null);
    try {
      const plan = await api.generateWorkout(token, {
        duration_minutes: duration,
        muscle_groups: muscles,
        difficulty,
      });
      navigation.navigate("Plan", { plan });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not generate workout");
    } finally {
      setBusy(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.label}>Duration</Text>
      <View style={styles.row}>
        {DURATIONS.map((d) => (
          <Chip key={d} active={duration === d} label={`${d} min`} onPress={() => setDuration(d)} />
        ))}
      </View>
      <Text style={styles.label}>Difficulty</Text>
      <View style={styles.row}>
        {DIFFICULTIES.map((d) => (
          <Chip key={d} active={difficulty === d} label={d} onPress={() => setDifficulty(d)} />
        ))}
      </View>
      <Text style={styles.label}>Muscle groups</Text>
      <View style={styles.row}>
        {MUSCLES.map((m) => (
          <Chip key={m} active={muscles.includes(m)} label={m} onPress={() => toggle(m)} />
        ))}
      </View>
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Pressable style={styles.button} onPress={draw} disabled={busy}>
        {busy ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Draw cards</Text>}
      </Pressable>
    </ScrollView>
  );
}

export function PlanScreen({ route, navigation }: { route: any; navigation: any }) {
  const plan = route.params.plan;
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>{plan.title}</Text>
      <Text style={styles.meta}>
        {plan.duration_minutes} min · {plan.difficulty} · {plan.source}
      </Text>
      {plan.exercises.map((ex: any, i: number) => (
        <FlipCard key={`${ex.exercise_id}-${i}`} exercise={ex} />
      ))}
      <Pressable style={styles.button} onPress={() => navigation.navigate("Player", { plan })}>
        <Text style={styles.buttonText}>Start workout</Text>
      </Pressable>
    </ScrollView>
  );
}

function Chip({
  label,
  active,
  onPress,
}: {
  label: string;
  active: boolean;
  onPress: () => void;
}) {
  return (
    <Pressable onPress={onPress} style={[styles.chip, active && styles.chipOn]}>
      <Text style={[styles.chipText, active && styles.chipTextOn]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24, backgroundColor: "#f4f1ea", paddingBottom: 48 },
  label: { fontWeight: "700", marginBottom: 8, marginTop: 12 },
  row: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: {
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: "white",
  },
  chipOn: { backgroundColor: "#222" },
  chipText: { color: "#222" },
  chipTextOn: { color: "white" },
  button: {
    backgroundColor: "#222",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginTop: 24,
  },
  buttonText: { color: "white", fontWeight: "600" },
  error: { color: "#8A3A3A", marginTop: 12 },
  title: { fontSize: 24, fontWeight: "700" },
  meta: { color: "#555", marginBottom: 16, marginTop: 4 },
});
