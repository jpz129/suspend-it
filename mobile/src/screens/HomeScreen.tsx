import { Pressable, StyleSheet, Text, View } from "react-native";

import { useAuth } from "../auth/AuthContext";

export function HomeScreen({ navigation }: { navigation: any }) {
  const { user } = useAuth();
  return (
    <View style={styles.container}>
      <Text style={styles.hello}>Hi {user?.name || user?.email}</Text>
      <Text style={styles.lede}>Draw a random card stack or ask for an AI session.</Text>
      <Pressable style={styles.card} onPress={() => navigation.navigate("DrawCard")}>
        <Text style={styles.cardTitle}>Draw a card</Text>
        <Text style={styles.cardBody}>Filter duration, muscles, difficulty.</Text>
      </Pressable>
      <Pressable style={styles.card} onPress={() => navigation.navigate("AiWorkout")}>
        <Text style={styles.cardTitle}>AI workout</Text>
        <Text style={styles.cardBody}>Describe a goal and available time.</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: "#f4f1ea" },
  hello: { fontSize: 26, fontWeight: "700", marginBottom: 8, marginTop: 12 },
  lede: { color: "#555", marginBottom: 24 },
  card: {
    backgroundColor: "white",
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
  },
  cardTitle: { fontSize: 20, fontWeight: "700", marginBottom: 6 },
  cardBody: { color: "#555" },
});
