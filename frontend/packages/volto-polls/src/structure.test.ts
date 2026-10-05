/**
 * Every component has a test and stories; every module in `config`,
 * `helpers`, `hooks`, `actions` and `reducers` has a test.
 *
 * The add-on has no coverage tool, so this is what keeps it tested.
 */
import { describe, it, expect } from 'vitest';
import { readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const srcDir = path.dirname(fileURLToPath(import.meta.url));

/** Every file below a folder, as paths relative to it. */
function walk(dir: string, prefix = ''): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const rel = path.join(prefix, entry.name);
    return entry.isDirectory() ? walk(path.join(dir, entry.name), rel) : [rel];
  });
}

const isSupport = (name: string) =>
  /\.(test|stories)\.tsx?$/.test(name) || /\.d\.ts$/.test(name);

function missing(folder: string, pattern: RegExp, suffixes: string[]) {
  const files = walk(path.join(srcDir, folder));
  const present = new Set(files);
  return files
    .filter((f) => pattern.test(f) && !isSupport(f))
    .flatMap((f) => {
      const stem = f.replace(/\.tsx?$/, '');
      return suffixes
        .filter((suffix) =>
          ['.ts', '.tsx'].every(
            (ext) => !present.has(`${stem}${suffix}${ext}`),
          ),
        )
        .map((suffix) => `${folder}/${stem}${suffix}`);
    });
}

describe('structure', () => {
  it('finds files to check, so an empty walk cannot pass', () => {
    expect(walk(path.join(srcDir, 'helpers')).length).toBeGreaterThan(0);
  });

  it('gives every component a test and stories', () => {
    expect(missing('components', /\.tsx$/, ['.test', '.stories'])).toEqual([]);
  });

  it.each(['config', 'helpers', 'hooks', 'actions', 'reducers'])(
    'gives every module in %s a test',
    (folder) => {
      expect(missing(folder, /\.tsx?$/, ['.test'])).toEqual([]);
    },
  );
});
