/**
 * Result sets shared by the chart tests and stories.
 */
import type { PollResult } from '../types/poll';

/** Build results from vote counts, with matching fractions. */
export function makeResults(...votes: number[]): PollResult[] {
  const total = votes.reduce((a, b) => a + b, 0);
  return votes.map((v, i) => ({
    option_id: i,
    description: `Option ${String.fromCharCode(65 + i)}`,
    votes: v,
    percentage: total ? v / total : 0,
  }));
}

/** The cases every chart covers. */
export const RESULT_SETS = {
  several: makeResults(5, 3, 2),
  aZeroOption: makeResults(4, 0, 1),
  allZero: makeResults(0, 0, 0),
  oneAtFull: makeResults(0, 7, 0),
};
