import { useQuery } from "@tanstack/react-query";
import { ScrollView, StyleSheet, Text, View } from "react-native";

import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function HistoryScreen() {
  const { token } = useAuth();
  const query = useQuery({
    queryKey: ["history"],
    queryFn: () => api.listHistory(token!),
    enabled: Boolean(token),
  });

  if (query.isLoading) {
    return (
      <View style={styles.container}>
        <Text>Loading…</Text>
      </View>
    );
  }
  if (query.isError) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>{(query.error as Error).message}</Text>
      </View>
    );
  }

  const rows = query.data ?? [];
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>History</Text>
      {rows.length === 0 ? <Text>No completed workouts yet.</Text> : null}
      {rows.map((row) => (
        <View key={row.id} style={styles.card}>
          <Text style={styles.name}>{row.workout_plan.title}</Text>
          <Text style={styles.meta}>
            {row.workout_plan.source} · {row.completed_at}
          </Text>
          <Text style={styles.meta}>{row.workout_plan.exercises.length} exercises</Text>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24, backgroundColor: "#f4f1ea", flexGrow: 1 },
  title: { fontSize: 26, fontWeight: "700", marginBottom: 16 },
  card: { backgroundColor: "white", borderRadius: 16, padding: 16, marginBottom: 12 },
  name: { fontSize: 18, fontWeight: "600" },
  meta: { color: "#555", marginTop: 4 },
  error: { color: "#8A3A3A" },
});
