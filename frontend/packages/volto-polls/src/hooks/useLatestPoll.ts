/**
 * The newest poll below a folder.
 * @module hooks/useLatestPoll
 */

import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getLatestPoll, latestPollKey } from '../actions/polls';
import { pollPath } from '../helpers/url';
import type { LatestPollEntry, PollsStoreState } from '../types/poll';

export interface UseLatestPollResult {
  /** Path of the poll to show; `null` when there is none, or not yet. */
  path: string | null;
  /** Its title. */
  title: string | null;
  /** Both searches that apply are answered. */
  loaded: boolean;
}

/**
 * Find the newest open poll, or with `includeClosed` the newest closed one
 * when no poll is open, as the 2.x portlet did.
 *
 * @param root The folder to search in, usually the navigation root.
 * @param includeClosed Fall back to closed polls.
 * @param enabled Search at all; a block showing a chosen poll does not.
 */
export function useLatestPoll(
  root: string,
  includeClosed: boolean,
  enabled = true,
): UseLatestPollResult {
  const dispatch = useDispatch();
  const latest = useSelector(
    (state: Partial<PollsStoreState>) => state.latestPolls ?? {},
  ) as Record<string, LatestPollEntry>;
  const open = latest[latestPollKey(root, 'open')];
  const closed = latest[latestPollKey(root, 'closed')];
  const needClosed = includeClosed && open?.loaded === true && !open.path;

  useEffect(() => {
    if (enabled) dispatch(getLatestPoll(root, 'open'));
  }, [dispatch, root, enabled]);

  useEffect(() => {
    if (enabled && needClosed) dispatch(getLatestPoll(root, 'closed'));
  }, [dispatch, root, enabled, needClosed]);

  if (!enabled) return { path: null, title: null, loaded: true };
  if (open?.path)
    return { path: pollPath(open.path), title: open.title, loaded: true };
  if (!needClosed)
    return { path: null, title: null, loaded: open?.loaded === true };
  return {
    path: closed?.path ? pollPath(closed.path) : null,
    title: closed?.path ? closed.title : null,
    loaded: closed?.loaded === true,
  };
}

export default useLatestPoll;
