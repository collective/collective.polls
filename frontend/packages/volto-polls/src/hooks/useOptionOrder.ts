/**
 * The order a poll's options are shown in.
 * @module hooks/useOptionOrder
 */

import { useEffect, useState } from 'react';
import { shuffled } from '../helpers/shuffle';
import type { PollOption } from '../types/poll';

/**
 * Put a poll's options in a random order, when the poll asks for it.
 *
 * The first render keeps the poll's own order, so what the server renders
 * and what the browser hydrates agree; the shuffle happens right after.
 * The order then stays put until the options change, so it does not move
 * while someone is choosing.
 *
 * @param options The poll's options, in the poll's order.
 * @param shuffle Whether the poll shuffles its options.
 * @returns The options, in the order to show them.
 */
export function useOptionOrder(
  options: PollOption[],
  shuffle: boolean,
): PollOption[] {
  const key = options.map((o) => `${o.option_id}:${o.description}`).join('|');
  const [order, setOrder] = useState<number[] | null>(null);

  useEffect(() => {
    setOrder(shuffle ? shuffled(options.map((o) => o.option_id)) : null);
    // The key stands for the options: a new array with the same options
    // must not shuffle them again.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, shuffle]);

  if (!order) return options;
  const byId = new Map(options.map((o) => [o.option_id, o]));
  const ordered = order
    .map((id) => byId.get(id))
    .filter((o): o is PollOption => Boolean(o));
  return ordered.length === options.length ? ordered : options;
}

export default useOptionOrder;
