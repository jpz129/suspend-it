/** Fixed illustration slugs — must match Component B. Do not invent new ones. */
export const ILLUSTRATION_SLUGS = [
  'row',
  'press',
  'squat',
  'lunge',
  'plank',
  'twist',
  'curl',
  'pull',
  'chest-fly',
  'core-crunch',
  'hinge',
  'jump',
  'stretch',
  'default',
] as const;

export type IllustrationSlug = (typeof ILLUSTRATION_SLUGS)[number];

export const FALLBACK_SLUG: IllustrationSlug = 'default';
