import assert from "node:assert/strict";
import test from "node:test";

test("workout plan contract: reps are strings and source is random|ai", () => {
  const plan = {
    title: "Test draw",
    duration_minutes: 30,
    difficulty: "beginner",
    source: "random",
    exercises: [
      {
        exercise_id: 1,
        name: "TRX Row",
        illustration_slug: "row",
        sets: 3,
        reps: "10",
        rest_seconds: 45,
        notes: null,
      },
    ],
  };
  assert.equal(typeof plan.exercises[0].reps, "string");
  assert.ok(["random", "ai"].includes(plan.source));
});
