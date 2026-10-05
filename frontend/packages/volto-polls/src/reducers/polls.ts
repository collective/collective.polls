/**
 * Reducers for polls, keyed by path so several polls can share a page.
 * @module reducers/polls
 */

import { GET_LATEST_POLL, GET_POLL, VOTE_POLL } from '../constants/ActionTypes';
import type {
  LatestPollEntry,
  PollEntry,
  PollError,
  PollState,
} from '../types/poll';

interface PollAction {
  type: string;
  path?: string;
  key?: string;
  result?: unknown;
  error?: unknown;
}

const EMPTY_POLL: PollEntry = {
  loading: false,
  loaded: false,
  error: null,
  data: null,
  voting: false,
  voteError: null,
};

const EMPTY_LATEST: LatestPollEntry = {
  loading: false,
  loaded: false,
  error: null,
  path: null,
  title: null,
};

/**
 * Turn what the API middleware reports for a failed request into an error.
 *
 * The middleware hands over the HTTP client's error: a `status`, and the
 * parsed body under `response.body`. The poll services answer
 * `{error: {type, message}}`; plone.rest answers `{type, message}`.
 *
 * @param error The middleware's `error`.
 */
export function toPollError(error: unknown): PollError {
  const err = (error ?? {}) as {
    status?: number;
    response?: { status?: number; body?: Record<string, any> };
  };
  const body = err.response?.body ?? {};
  const detail = body.error ?? body;
  return {
    status: err.status ?? err.response?.status,
    type: typeof detail.type === 'string' ? detail.type : undefined,
    message: typeof detail.message === 'string' ? detail.message : undefined,
  };
}

/**
 * The state of every poll fetched so far, by path.
 *
 * A failed vote keeps the poll's last known state.
 */
export function polls(
  state: Record<string, PollEntry> = {},
  action: PollAction = { type: '' },
): Record<string, PollEntry> {
  if (!action.path) return state;
  const entry = state[action.path] ?? EMPTY_POLL;
  const update = (changes: Partial<PollEntry>) => ({
    ...state,
    [action.path as string]: { ...entry, ...changes },
  });
  switch (action.type) {
    case `${GET_POLL}_PENDING`:
      return update({ loading: true, error: null });
    case `${GET_POLL}_SUCCESS`:
      return update({
        loading: false,
        loaded: true,
        data: action.result as PollState,
      });
    case `${GET_POLL}_FAIL`:
      return update({
        loading: false,
        loaded: false,
        error: toPollError(action.error),
      });
    case `${VOTE_POLL}_PENDING`:
      return update({ voting: true, voteError: null });
    case `${VOTE_POLL}_SUCCESS`:
      return update({
        voting: false,
        loaded: true,
        data: action.result as PollState,
      });
    case `${VOTE_POLL}_FAIL`:
      return update({ voting: false, voteError: toPollError(action.error) });
    default:
      return state;
  }
}

/** The newest poll found by each search, by search key. */
export function latestPolls(
  state: Record<string, LatestPollEntry> = {},
  action: PollAction = { type: '' },
): Record<string, LatestPollEntry> {
  if (!action.key) return state;
  const entry = state[action.key] ?? EMPTY_LATEST;
  const update = (changes: Partial<LatestPollEntry>) => ({
    ...state,
    [action.key as string]: { ...entry, ...changes },
  });
  switch (action.type) {
    case `${GET_LATEST_POLL}_PENDING`:
      return update({ loading: true, error: null });
    case `${GET_LATEST_POLL}_SUCCESS`: {
      const result = action.result as {
        items?: { '@id': string; title?: string }[];
      };
      const item = result?.items?.[0];
      return update({
        loading: false,
        loaded: true,
        path: item?.['@id'] ?? null,
        title: item?.title ?? null,
      });
    }
    case `${GET_LATEST_POLL}_FAIL`:
      return update({
        loading: false,
        loaded: true,
        path: null,
        title: null,
        error: toPollError(action.error),
      });
    default:
      return state;
  }
}
