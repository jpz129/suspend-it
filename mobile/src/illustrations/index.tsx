import { StyleSheet, Text, View } from "react-native";

import type { IllustrationSlug } from "../types/api";

export const SLUG_COLORS: Record<IllustrationSlug, string> = {
  row: "#2E6B8A",
  press: "#C45C26",
  squat: "#3D7A4A",
  lunge: "#6B4C9A",
  plank: "#B4532A",
  twist: "#1F7A6B",
  curl: "#A33B5D",
  pull: "#2F5F99",
  "chest-fly": "#C46B3A",
  "core-crunch": "#8A3A3A",
  hinge: "#4A6B2E",
  jump: "#C49A1A",
  stretch: "#5A8A9A",
  default: "#5C6370",
};

export function resolveSlug(slug: string): IllustrationSlug {
  return (slug in SLUG_COLORS ? slug : "default") as IllustrationSlug;
}

export function IllustrationCard({
  slug,
  label,
}: {
  slug: string;
  label?: string;
}) {
  const resolved = resolveSlug(slug);
  return (
    <View style={[styles.card, { backgroundColor: SLUG_COLORS[resolved] }]}>
      <Text style={styles.kicker}>{resolved.toUpperCase()}</Text>
      <View style={styles.figure}>
        <View style={styles.head} />
        <View style={styles.body} />
        <View style={styles.armRow}>
          <View style={styles.limb} />
          <View style={styles.limb} />
        </View>
        <View style={styles.armRow}>
          <View style={[styles.limb, styles.leg]} />
          <View style={[styles.limb, styles.leg]} />
        </View>
      </View>
      {label ? <Text style={styles.label}>{label}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 20,
    minHeight: 220,
    padding: 20,
    justifyContent: "space-between",
  },
  kicker: {
    color: "white",
    letterSpacing: 2,
    fontWeight: "700",
    fontSize: 14,
  },
  figure: {
    alignItems: "center",
    gap: 8,
  },
  head: {
    width: 28,
    height: 28,
    borderRadius: 14,
    borderWidth: 3,
    borderColor: "white",
  },
  body: {
    width: 3,
    height: 54,
    backgroundColor: "white",
  },
  armRow: {
    flexDirection: "row",
    gap: 28,
    marginTop: -40,
  },
  limb: {
    width: 36,
    height: 3,
    backgroundColor: "white",
    transform: [{ rotate: "25deg" }],
  },
  leg: {
    marginTop: 70,
    width: 40,
  },
  label: {
    color: "white",
    fontSize: 18,
    fontWeight: "600",
    textAlign: "center",
  },
});
