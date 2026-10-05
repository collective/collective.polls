import { describe, it, expect } from 'vitest';
import {
  COLOR_COUNT,
  formatPercent,
  optionColor,
  wholePercents,
} from './results';
import type { PollResult } from '../types/poll';

function results(...votes: number[]): PollResult[] {
  return votes.map((v, i) => ({
    option_id: i,
    description: `Option ${i}`,
    votes: v,
    percentage: 0,
  }));
}

describe('wholePercents', () => {
  it.each([
    [
      [1, 1, 1],
      [34, 33, 33],
    ],
    [
      [2, 1],
      [67, 33],
    ],
    [
      [1, 0],
      [100, 0],
    ],
    [
      [0, 0, 0],
      [0, 0, 0],
    ],
    [
      [1, 1, 1, 1, 1, 1, 1],
      [15, 15, 14, 14, 14, 14, 14],
    ],
    [
      [3, 3, 1],
      [43, 43, 14],
    ],
  ])('splits %j into %j', (votes, expected) => {
    expect(wholePercents(results(...votes))).toEqual(expected);
  });

  it('always adds up to 100 once someone voted', () => {
    for (let seed = 1; seed < 200; seed++) {
      const votes = [seed % 7, (seed * 3) % 11, (seed * 5) % 13, 1];
      const sum = wholePercents(results(...votes)).reduce((a, b) => a + b, 0);
      expect(sum).toBe(100);
    }
  });

  it('copes with no options', () => {
    expect(wholePercents([])).toEqual([]);
  });
});

describe('formatPercent', () => {
  it('formats for the language', () => {
    expect(formatPercent(67, 'en')).toBe('67%');
    expect(formatPercent(67, 'pt-BR')).toMatch(/^67\s?%$/);
  });
});

describe('optionColor', () => {
  it('cycles through the theme colors', () => {
    expect(optionColor(0)).toBe('var(--polls-color-1)');
    expect(optionColor(COLOR_COUNT)).toBe('var(--polls-color-1)');
    expect(optionColor(COLOR_COUNT - 1)).toBe(
      `var(--polls-color-${COLOR_COUNT})`,
    );
  });
});
