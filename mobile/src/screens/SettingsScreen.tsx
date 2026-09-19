import { Pressable, StyleSheet, Text, View } from "react-native";

import { API_URL, USE_MOCKS } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export function SettingsScreen() {
  const { logout, user } = useAuth();
  return (
    <View style={styles.container}>
      <Text style={styles.title}>About</Text>
      <Text style={styles.body}>{user?.email}</Text>
      <Text style={styles.body}>API: {USE_MOCKS ? "mock fixtures" : API_URL}</Text>
      <Text style={styles.attr}>Exercise data from wger.de</Text>
      <Pressable style={styles.button} onPress={logout}>
        <Text style={styles.buttonText}>Log out</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: "#f4f1ea" },
  title: { fontSize: 26, fontWeight: "700", marginBottom: 12, marginTop: 12 },
  body: { color: "#555", marginBottom: 8 },
  attr: { marginTop: 24, fontSize: 14, color: "#333" },
  button: {
    backgroundColor: "#222",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginTop: 32,
  },
  buttonText: { color: "white", fontWeight: "600" },
});
