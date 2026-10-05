import { afterEach, describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import useOptionOrder from './useOptionOrder';
import type { PollOption } from '../types/poll';

const OPTIONS: PollOption[] = [
  { option_id: 0, description: 'Red' },
  { option_id: 1, description: 'Green' },
  { option_id: 2, description: 'Blue' },
];

const ids = (options: PollOption[]) => options.map((o) => o.option_id);

function setup(shuffle: boolean, options: PollOption[] = OPTIONS) {
  return renderHook(({ opts, flag }) => useOptionOrder(opts, flag), {
    initialProps: { opts: options, flag: shuffle },
  });
}

describe('useOptionOrder', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('keeps the poll order when the poll does not shuffle', () => {
    const random = vi.spyOn(Math, 'random');
    const { result } = setup(false);
    expect(ids(result.current)).toEqual([0, 1, 2]);
    expect(random).not.toHaveBeenCalled();
  });

  it('shuffles when the poll asks for it', () => {
    vi.spyOn(Math, 'random').mockReturnValue(0);
    const { result } = setup(true);
    expect(ids(result.current)).toEqual([1, 2, 0]);
  });

  it('keeps the order while the options stay the same', () => {
    const random = vi.spyOn(Math, 'random').mockReturnValue(0);
    const { result, rerender } = setup(true);
    rerender({ opts: OPTIONS.map((o) => ({ ...o })), flag: true });
    expect(ids(result.current)).toEqual([1, 2, 0]);
    expect(random).toHaveBeenCalledTimes(2);
  });

  it('shuffles again when the options change', () => {
    vi.spyOn(Math, 'random').mockReturnValue(0);
    const { result, rerender } = setup(true);
    const more = [...OPTIONS, { option_id: 3, description: 'Black' }];
    rerender({ opts: more, flag: true });
    expect(ids(result.current)).toEqual([1, 2, 3, 0]);
  });

  it('goes back to the poll order when shuffling is turned off', () => {
    vi.spyOn(Math, 'random').mockReturnValue(0);
    const { result, rerender } = setup(true);
    rerender({ opts: OPTIONS, flag: false });
    expect(ids(result.current)).toEqual([0, 1, 2]);
  });
});
