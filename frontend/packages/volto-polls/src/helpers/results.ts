/**
 * Arithmetic and formatting for poll results.
 * @module helpers/results
 */

import type { PollResult } from '../types/poll';

/** How many chart colors the theme declares. */
export const COLOR_COUNT = 8;

/**
 * Round each option's share to whole percents that add up to 100.
 *
 * Plain rounding can give 99 or 101 in total (three equal thirds round to
 * 33 each). The largest remainder method hands the missing points to the
 * options that lost the most to rounding, in option order on ties.
 *
 * @param results The results of a poll.
 * @returns One whole percent per result; all zero while nobody voted.
 */
export function wholePercents(results: PollResult[]): number[] {
  const total = results.reduce((sum, r) => sum + r.votes, 0);
  if (total === 0) return results.map(() => 0);
  const exact = results.map((r) => (r.votes * 100) / total);
  const floors = exact.map(Math.floor);
  let missing = 100 - floors.reduce((sum, n) => sum + n, 0);
  const order = exact
    .map((value, index) => ({ index, remainder: value - floors[index] }))
    .sort((a, b) => b.remainder - a.remainder || a.index - b.index);
  for (const { index } of order) {
    if (missing === 0) break;
    floors[index] += 1;
    missing -= 1;
  }
  return floors;
}

/**
 * Format a whole percent for the reader's language.
 *
 * @param percent A whole percent, `0` to `100`.
 * @param locale The language to format for.
 */
export function formatPercent(percent: number, locale: string): string {
  return new Intl.NumberFormat(locale, {
    style: 'percent',
    maximumFractionDigits: 0,
  }).format(percent / 100);
}

/**
 * The CSS color of the n-th option.
 *
 * Colors come from custom properties, so a theme can change them.
 *
 * @param index The option's position.
 */
export function optionColor(index: number): string {
  return `var(--polls-color-${(index % COLOR_COUNT) + 1})`;
}
