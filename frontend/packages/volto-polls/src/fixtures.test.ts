/**
 * The fixtures are copies of the backend's example payloads, which the
 * backend tests prove are what `@poll` really answers. A fixture edited on
 * this side only would let the two halves drift apart.
 */
import { describe, it, expect } from 'vitest';
import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const srcDir = path.dirname(fileURLToPath(import.meta.url));
const fixtures = path.join(srcDir, '__fixtures__');
const examples = path.resolve(
  srcDir,
  '../../../../backend/tests/_resources/poll-examples',
);

const list = (dir: string) =>
  readdirSync(dir)
    .filter((f) => f.endsWith('.json'))
    .sort();

describe('fixtures', () => {
  it('has the same files as the backend examples', () => {
    expect(list(examples).length).toBeGreaterThan(0);
    expect(list(fixtures)).toEqual(list(examples));
  });

  it.each(list(examples))('%s is identical to the backend example', (name) => {
    expect(readFileSync(path.join(fixtures, name), 'utf8')).toBe(
      readFileSync(path.join(examples, name), 'utf8'),
    );
  });
});
