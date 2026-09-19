import fs from 'node:fs';
import path from 'node:path';

import { ILLUSTRATION_SLUGS } from '../../illustrations/slugs';

describe('bundled illustrations', () => {
  it('has a PNG for every required slug', () => {
    const dir = path.resolve(__dirname, '../../../assets/illustrations');
    for (const slug of ILLUSTRATION_SLUGS) {
      const file = path.join(dir, `${slug}.png`);
      expect(fs.existsSync(file)).toBe(true);
    }
  });
});
