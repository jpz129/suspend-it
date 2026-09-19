import type { ImageSourcePropType } from 'react-native';

import { FALLBACK_SLUG, type IllustrationSlug } from './slugs';

const ILLUSTRATIONS: Record<IllustrationSlug, ImageSourcePropType> = {
  row: require('../../assets/illustrations/row.png'),
  press: require('../../assets/illustrations/press.png'),
  squat: require('../../assets/illustrations/squat.png'),
  lunge: require('../../assets/illustrations/lunge.png'),
  plank: require('../../assets/illustrations/plank.png'),
  twist: require('../../assets/illustrations/twist.png'),
  curl: require('../../assets/illustrations/curl.png'),
  pull: require('../../assets/illustrations/pull.png'),
  'chest-fly': require('../../assets/illustrations/chest-fly.png'),
  'core-crunch': require('../../assets/illustrations/core-crunch.png'),
  hinge: require('../../assets/illustrations/hinge.png'),
  jump: require('../../assets/illustrations/jump.png'),
  stretch: require('../../assets/illustrations/stretch.png'),
  default: require('../../assets/illustrations/default.png'),
};

export function getIllustration(slug: string | null | undefined): ImageSourcePropType {
  if (slug && slug in ILLUSTRATIONS) {
    return ILLUSTRATIONS[slug as IllustrationSlug];
  }
  return ILLUSTRATIONS[FALLBACK_SLUG];
}
