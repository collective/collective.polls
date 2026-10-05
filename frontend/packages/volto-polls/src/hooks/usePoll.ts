/**
 * The state of one poll, and voting in it.
 * @module hooks/usePoll
 */

import { useCallback, useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getPoll, votePoll } from '../actions/polls';
import { hasVotedCookie } from '../helpers/cookie';
import type {
  PollEntry,
  PollError,
  PollState,
  PollsStoreState,
} from '../types/poll';

export interface UsePollResult {
  poll: PollState | null;
  loading: boolean;
  loaded: boolean;
  error: PollError | null;
  /** Vote for options; resolves once the vote is answered either way. */
  vote: (optionIds: number[]) => Promise<void>;
  voting: boolean;
  voteError: PollError | null;
  /** From the backend for members, from the cookie for anonymous visitors. */
  hasVoted: boolean;
  /** Open, the user may vote, and has not voted yet. */
  canVoteNow: boolean;
}

/**
 * Fetch a poll and expose its state.
 *
 * The fetch happens in an effect, so never while rendering on the server:
 * the answer depends on who asks, and on a cookie only the browser has.
 *
 * @param path The poll's path, relative to the site; empty for none.
 */
export function usePoll(path: string): UsePollResult {
  const dispatch = useDispatch();
  const entry = useSelector(
    (state: Partial<PollsStoreState>) => state.polls?.[path],
  ) as PollEntry | undefined;
  const poll = entry?.data ?? null;
  const [cookieVoted, setCookieVoted] = useState(false);

  useEffect(() => {
    if (path) dispatch(getPoll(path));
  }, [dispatch, path]);

  // Read again whenever the poll changes: a vote sets the cookie.
  useEffect(() => {
    setCookieVoted(poll ? hasVotedCookie(poll.uid) : false);
  }, [poll]);

  const vote = useCallback(
    async (optionIds: number[]) => {
      try {
        await dispatch(votePoll(path, optionIds) as any);
      } catch {
        // The failure is in the store as `voteError`.
      }
    },
    [dispatch, path],
  );

  const hasVoted =
    typeof poll?.has_voted === 'boolean' ? poll.has_voted : cookieVoted;
  const canVoteNow = Boolean(
    poll && poll.can_vote && !hasVoted && poll.state === 'open',
  );

  return {
    poll,
    loading: entry?.loading ?? false,
    loaded: entry?.loaded ?? false,
    error: entry?.error ?? null,
    vote,
    voting: entry?.voting ?? false,
    voteError: entry?.voteError ?? null,
    hasVoted,
    canVoteNow,
  };
}

export default usePoll;
