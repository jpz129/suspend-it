import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";

import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { IllustrationCard } from "../illustrations";
import type { WorkoutExercise, WorkoutPlan } from "../types/api";

export function WorkoutPlayerScreen({ route, navigation }: { route: any; navigation: any }) {
  const plan: WorkoutPlan = route.params.plan;
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [done, setDone] = useState<Record<number, boolean>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggle = (index: number) => {
    setDone((curr) => ({ ...curr, [index]: !curr[index] }));
  };

  const finish = async () => {
    if (!token) return;
    setSaving(true);
    setError(null);
    try {
      await api.saveHistory(token, {
        workout_plan: plan,
        completed_at: new Date().toISOString(),
        notes: null,
      });
      await queryClient.invalidateQueries({ queryKey: ["history"] });
      navigation.navigate("HistoryTab");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save history");
    } finally {
      setSaving(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>{plan.title}</Text>
      {plan.exercises.map((ex: WorkoutExercise, index: number) => (
        <Pressable key={`${ex.exercise_id}-${index}`} onPress={() => toggle(index)} style={styles.row}>
          <View style={[styles.check, done[index] && styles.checkOn]} />
          <View style={styles.cardWrap}>
            <IllustrationCard slug={ex.illustration_slug} />
          </View>
          <View style={styles.copy}>
            <Text style={[styles.name, done[index] && styles.struck]}>{ex.name}</Text>
            <Text style={styles.meta}>
              {ex.sets} × {ex.reps} · rest {ex.rest_seconds}s
            </Text>
          </View>
        </Pressable>
      ))}
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Pressable style={styles.button} onPress={finish} disabled={saving}>
        <Text style={styles.buttonText}>{saving ? "Saving…" : "Finish & save"}</Text>
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24, backgroundColor: "#f4f1ea", paddingBottom: 48 },
  title: { fontSize: 24, fontWeight: "700", marginBottom: 16 },
  row: { flexDirection: "row", gap: 12, marginBottom: 16, alignItems: "center" },
  check: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: "#222",
  },
  checkOn: { backgroundColor: "#222" },
  cardWrap: { width: 72, height: 96, overflow: "hidden", borderRadius: 8 },
  copy: { flex: 1 },
  name: { fontSize: 16, fontWeight: "600" },
  struck: { textDecorationLine: "line-through", color: "#888" },
  meta: { color: "#555", marginTop: 4 },
  button: {
    backgroundColor: "#222",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginTop: 12,
  },
  buttonText: { color: "white", fontWeight: "600" },
  error: { color: "#8A3A3A", marginBottom: 8 },
});
