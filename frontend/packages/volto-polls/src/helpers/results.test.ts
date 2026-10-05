import { describe, it, expect } from 'vitest';
import {
  COLOR_COUNT,
  formatPercent,
  optionColor,
  wholePercents,
} from './results';
import type { PollResult } from '../types/poll';

/** Single choice results: each share is of all the votes. */
function results(...votes: number[]): PollResult[] {
  const total = votes.reduce((a, b) => a + b, 0);
  return votes.map((v, i) => ({
    option_id: i,
    description: `Option ${i}`,
    votes: v,
    percentage: total ? v / total : 0,
  }));
}

/** Multiple choice results: each share is of the voters. */
function sharesOfVoters(voters: number, ...votes: number[]): PollResult[] {
  return votes.map((v, i) => ({
    option_id: i,
    description: `Option ${i}`,
    votes: v,
    percentage: v / voters,
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

  it('rounds shares of voters on their own, past 100 in total', () => {
    // Three voters, two of them picked option 0 and option 2.
    expect(wholePercents(sharesOfVoters(3, 2, 1, 2))).toEqual([67, 33, 67]);
  });

  it('uses the share the backend reports, not one of its own', () => {
    expect(wholePercents(sharesOfVoters(2, 2, 2))).toEqual([100, 100]);
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
