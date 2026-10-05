import { describe, it, expect } from 'vitest';
import { shuffled } from './shuffle';

describe('shuffled', () => {
  it('keeps every item, and the list given as it was', () => {
    const items = [0, 1, 2, 3, 4];
    const result = shuffled(items);
    expect([...result].sort()).toEqual(items);
    expect(items).toEqual([0, 1, 2, 3, 4]);
    expect(result).not.toBe(items);
  });

  it('follows the random source', () => {
    // Always the lowest index: each step swaps with the first item.
    expect(shuffled([0, 1, 2, 3], () => 0)).toEqual([1, 2, 3, 0]);
    // Always the highest index: nothing moves.
    expect(shuffled([0, 1, 2, 3], () => 0.999)).toEqual([0, 1, 2, 3]);
  });

  it('gives every order of three items', () => {
    const seen = new Set<string>();
    for (let n = 0; n < 500; n++) seen.add(shuffled([0, 1, 2]).join());
    expect(seen.size).toBe(6);
  });

  it('copes with empty and single lists', () => {
    expect(shuffled([])).toEqual([]);
    expect(shuffled(['only'])).toEqual(['only']);
  });
});
