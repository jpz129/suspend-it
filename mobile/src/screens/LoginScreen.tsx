import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { useAuth } from "../auth/AuthContext";

export function LoginScreen({ navigation }: { navigation: any }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("demo@suspend.it");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const onSubmit = async () => {
    setBusy(true);
    setError(null);
    try {
      await login(email.trim(), password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>suspend-it</Text>
      <Text style={styles.sub}>TRX workouts, drawn like a card deck.</Text>
      <TextInput
        autoCapitalize="none"
        keyboardType="email-address"
        placeholder="Email"
        style={styles.input}
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        placeholder="Password"
        secureTextEntry
        style={styles.input}
        value={password}
        onChangeText={setPassword}
      />
      {error ? <Text style={styles.error}>{error}</Text> : null}
      <Pressable style={styles.button} onPress={onSubmit} disabled={busy}>
        {busy ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Log in</Text>}
      </Pressable>
      <Pressable onPress={() => navigation.navigate("Register")}>
        <Text style={styles.link}>Create an account</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: "center", backgroundColor: "#f4f1ea" },
  title: { fontSize: 32, fontWeight: "700", marginBottom: 8 },
  sub: { color: "#555", marginBottom: 24 },
  input: {
    backgroundColor: "white",
    borderRadius: 10,
    padding: 14,
    marginBottom: 12,
    fontSize: 16,
  },
  button: {
    backgroundColor: "#222",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginTop: 8,
  },
  buttonText: { color: "white", fontWeight: "600" },
  link: { textAlign: "center", marginTop: 16, color: "#2E6B8A" },
  error: { color: "#8A3A3A", marginBottom: 8 },
});
