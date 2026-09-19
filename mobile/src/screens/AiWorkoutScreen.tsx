import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { api } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function AiWorkoutScreen({ navigation }: { navigation: any }) {
  const { token } = useAuth();
  const [goals, setGoals] = useState("stronger back and core");
  const [minutes, setMinutes] = useState("20");
  const [equipment, setEquipment] = useState("TRX");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generate = async () => {
    if (!token) return;
    setBusy(true);
    setError(null);
    try {
      const plan = await api.generateAiWorkout(token, {
        goals,
        available_time_minutes: Number(minutes) || 20,
        equipment: equipment.split(",").map((s) => s.trim()).filter(Boolean),
        notes: notes.trim() || null,
      });
      navigation.navigate("Plan", { plan });
    } catch (err) {
      setError(err instanceof Error ? err.message : "AI generate failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.label}>Goals</Text>
      <TextInput style={styles.input} value={goals} onChangeText={setGoals} />
      <Text style={styles.label}>Available minutes</Text>
      <TextInput
        style={styles.input}
        keyboardType="number-pad"
        value={minutes}
        onChangeText={setMinutes}
      />
      <Text style={styles.label}>Equipment (comma separated)</Text>
      <TextInput style={styles.input} value={equipment} onChangeText={setEquipment} />
      <Text style={styles.label}>Notes</Text>
      <TextInput
        style={[styles.input, styles.area]}
        value={notes}
        onChangeText={setNotes}
        multiline
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Pressable style={styles.button} onPress={generate} disabled={busy}>
        {busy ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Generate</Text>}
      </Pressable>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 24, backgroundColor: "#f4f1ea" },
  label: { fontWeight: "700", marginBottom: 8, marginTop: 12 },
  input: {
    backgroundColor: "white",
    borderRadius: 10,
    padding: 14,
    fontSize: 16,
  },
  area: { minHeight: 80, textAlignVertical: "top" },
  button: {
    backgroundColor: "#222",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginTop: 24,
  },
  buttonText: { color: "white", fontWeight: "600" },
  error: { color: "#8A3A3A", marginTop: 12 },
});
