/**
 * Actions for polls. Each goes through Volto's API middleware.
 * @module actions/polls
 */

import { GET_LATEST_POLL, GET_POLL, VOTE_POLL } from '../constants/ActionTypes';
import { POLL_TYPE } from '../constants/poll';

/**
 * Read the state of a poll, and its results when the caller may see them.
 *
 * @param path The poll's path, relative to the site.
 */
export function getPoll(path: string) {
  return {
    type: GET_POLL,
    path,
    request: { op: 'get', path: `${path}/@poll` },
  };
}

/**
 * Vote in a poll. The answer is the new state of the poll.
 *
 * @param path The poll's path, relative to the site.
 * @param optionId The id of the option voted for.
 */
export function votePoll(path: string, optionId: number) {
  return {
    type: VOTE_POLL,
    path,
    request: {
      op: 'post',
      path: `${path}/@vote`,
      data: { option_id: optionId },
    },
  };
}

/** The key the newest poll of a folder and state is stored under. */
export function latestPollKey(root: string, state: 'open' | 'closed'): string {
  return `${root}|${state}`;
}

/**
 * Find the newest poll in a workflow state, below a folder.
 *
 * @param root The folder to search in, usually the navigation root.
 * @param state `open`, or `closed` for the fallback when nothing is open.
 */
export function getLatestPoll(root: string, state: 'open' | 'closed') {
  const query = new URLSearchParams({
    portal_type: POLL_TYPE,
    review_state: state,
    sort_on: 'created',
    sort_order: 'descending',
    b_size: '1',
  });
  return {
    type: GET_LATEST_POLL,
    key: latestPollKey(root, state),
    request: { op: 'get', path: `${root}/@search?${query.toString()}` },
  };
}
