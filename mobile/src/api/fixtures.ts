import { FALLBACK_SLUG, ILLUSTRATION_SLUGS, type IllustrationSlug } from '../illustrations/slugs';
import type { Difficulty } from './types';

export type FixtureExercise = {
  id: number;
  name: string;
  muscle_group: string;
  difficulty: Difficulty;
  equipment: string;
  instructions: string;
  illustration_slug: IllustrationSlug;
  source: 'curated';
};

export const DEMO_USER = {
  email: 'demo@suspend.it',
  password: 'password123',
  name: 'Demo Athlete',
};

export const FIXTURE_EXERCISES: FixtureExercise[] = [
  {
    id: 1,
    name: 'TRX Row',
    muscle_group: 'back',
    difficulty: 'beginner',
    equipment: 'suspension trainer',
    instructions: 'Lean back, pull straps to ribs, squeeze shoulder blades.',
    illustration_slug: 'row',
    source: 'curated',
  },
  {
    id: 2,
    name: 'TRX Chest Press',
    muscle_group: 'chest',
    difficulty: 'beginner',
    equipment: 'suspension trainer',
    instructions: 'Face away from the anchor and press out from a plank-like lean.',
    illustration_slug: 'press',
    source: 'curated',
  },
  {
    id: 3,
    name: 'TRX Squat',
    muscle_group: 'legs',
    difficulty: 'beginner',
    equipment: 'suspension trainer',
    instructions: 'Hold the handles, sit the hips back, and stand up tall.',
    illustration_slug: 'squat',
    source: 'curated',
  },
  {
    id: 4,
    name: 'TRX Lunge',
    muscle_group: 'legs',
    difficulty: 'intermediate',
    equipment: 'suspension trainer',
    instructions: 'Step back into a lunge while keeping the straps taut.',
    illustration_slug: 'lunge',
    source: 'curated',
  },
  {
    id: 5,
    name: 'TRX Plank',
    muscle_group: 'core',
    difficulty: 'intermediate',
    equipment: 'suspension trainer',
    instructions: 'Feet in the cradles, brace the core, hold a straight line.',
    illustration_slug: 'plank',
    source: 'curated',
  },
  {
    id: 6,
    name: 'TRX Hip Twist',
    muscle_group: 'core',
    difficulty: 'advanced',
    equipment: 'suspension trainer',
    instructions: 'From a plank, rotate the hips slowly without collapsing.',
    illustration_slug: 'twist',
    source: 'curated',
  },
  {
    id: 7,
    name: 'TRX Biceps Curl',
    muscle_group: 'arms',
    difficulty: 'beginner',
    equipment: 'suspension trainer',
    instructions: 'Supinate the palms and curl the handles toward the temples.',
    illustration_slug: 'curl',
    source: 'curated',
  },
  {
    id: 8,
    name: 'TRX Y-Pull',
    muscle_group: 'shoulders',
    difficulty: 'intermediate',
    equipment: 'suspension trainer',
    instructions: 'Pull the handles overhead into a Y while staying tall.',
    illustration_slug: 'pull',
    source: 'curated',
  },
  {
    id: 9,
    name: 'TRX Chest Fly',
    muscle_group: 'chest',
    difficulty: 'advanced',
    equipment: 'suspension trainer',
    instructions: 'Open the arms wide, then squeeze the chest to close.',
    illustration_slug: 'chest-fly',
    source: 'curated',
  },
  {
    id: 10,
    name: 'TRX Crunch',
    muscle_group: 'core',
    difficulty: 'beginner',
    equipment: 'suspension trainer',
    instructions: 'Feet in the cradles, draw the knees toward the chest.',
    illustration_slug: 'core-crunch',
    source: 'curated',
  },
  {
    id: 11,
    name: 'TRX Hip Hinge',
    muscle_group: 'back',
    difficulty: 'intermediate',
    equipment: 'suspension trainer',
    instructions: 'Push the hips back with a flat spine, then stand and squeeze.',
    illustration_slug: 'hinge',
    source: 'curated',
  },
  {
    id: 12,
    name: 'TRX Squat Jump',
    muscle_group: 'legs',
    difficulty: 'advanced',
    equipment: 'suspension trainer',
    instructions: 'Sit into a squat and explode up, landing softly.',
    illustration_slug: 'jump',
    source: 'curated',
  },
  {
    id: 13,
    name: 'TRX Overhead Stretch',
    muscle_group: 'shoulders',
    difficulty: 'beginner',
    equipment: 'suspension trainer',
    instructions: 'Lean into the straps and open the chest toward the ceiling.',
    illustration_slug: 'stretch',
    source: 'curated',
  },
  {
    id: 14,
    name: 'TRX Low Row',
    muscle_group: 'back',
    difficulty: 'advanced',
    equipment: 'suspension trainer',
    instructions: 'Walk the feet forward and row from a steeper angle.',
    illustration_slug: 'row',
    source: 'curated',
  },
  {
    id: 15,
    name: 'TRX Triceps Press',
    muscle_group: 'arms',
    difficulty: 'intermediate',
    equipment: 'suspension trainer',
    instructions: 'Keep elbows high and extend the handles forward.',
    illustration_slug: 'press',
    source: 'curated',
  },
];

export const ALL_SLUGS = ILLUSTRATION_SLUGS;
export const DEFAULT_SLUG = FALLBACK_SLUG;
