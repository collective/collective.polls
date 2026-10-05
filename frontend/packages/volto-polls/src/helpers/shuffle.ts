/**
 * Random order for a poll's options.
 * @module helpers/shuffle
 */

/**
 * Return a shuffled copy of a list, leaving the list as it was.
 *
 * Fisher–Yates: every order is equally likely, given a uniform `random`.
 *
 * @param items The list to shuffle.
 * @param random A source of numbers in `[0, 1)`; `Math.random` by default.
 */
export function shuffled<T>(
  items: readonly T[],
  random: () => number = Math.random,
): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}
