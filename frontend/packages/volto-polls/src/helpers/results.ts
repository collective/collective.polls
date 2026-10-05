/**
 * Arithmetic and formatting for poll results.
 * @module helpers/results
 */

import type { PollResult } from '../types/poll';

/** How many chart colors the theme declares. */
export const COLOR_COUNT = 8;

/**
 * Round each option's share, as the backend reports it, to whole percents.
 *
 * In a single choice poll the shares add up to 100, and so must the whole
 * percents: plain rounding can give 99 or 101 in total (three equal thirds
 * round to 33 each). The largest remainder method hands the missing points
 * to the options that lost the most to rounding, in option order on ties.
 *
 * In a multiple choice poll each share is of the voters, so they can add up
 * past 100; each is then rounded on its own.
 *
 * @param results The results of a poll.
 * @returns One whole percent per result; all zero while nobody voted.
 */
export function wholePercents(results: PollResult[]): number[] {
  const exact = results.map((r) => r.percentage * 100);
  const sum = exact.reduce((a, b) => a + b, 0);
  if (sum === 0) return results.map(() => 0);
  if (Math.abs(sum - 100) > 1e-6) return exact.map(Math.round);
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
