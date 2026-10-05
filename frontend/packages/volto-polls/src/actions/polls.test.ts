import { describe, it, expect } from 'vitest';
import { getLatestPoll, getPoll, latestPollKey, votePoll } from './polls';
import { GET_LATEST_POLL, GET_POLL, VOTE_POLL } from '../constants/ActionTypes';

describe('getPoll', () => {
  it('reads @poll below the poll', () => {
    expect(getPoll('/folder/a-poll')).toEqual({
      type: GET_POLL,
      path: '/folder/a-poll',
      request: { op: 'get', path: '/folder/a-poll/@poll' },
    });
  });
});

describe('votePoll', () => {
  it('posts the option ids to @vote', () => {
    expect(votePoll('/a-poll', [0, 2])).toEqual({
      type: VOTE_POLL,
      path: '/a-poll',
      request: {
        op: 'post',
        path: '/a-poll/@vote',
        data: { option_ids: [0, 2] },
      },
    });
  });

  it('sends option 0, which is falsy, as is', () => {
    expect(votePoll('/a-poll', [0]).request.data).toEqual({ option_ids: [0] });
  });
});

describe('getLatestPoll', () => {
  it('searches for the newest poll in a state', () => {
    const action = getLatestPoll('/en', 'open');
    expect(action.type).toBe(GET_LATEST_POLL);
    expect(action.key).toBe('/en|open');
    const [path, search] = action.request.path.split('?');
    expect(path).toBe('/en/@search');
    expect(Object.fromEntries(new URLSearchParams(search))).toEqual({
      portal_type: 'collective.polls.poll',
      review_state: 'open',
      sort_on: 'created',
      sort_order: 'descending',
      b_size: '1',
    });
  });

  it('searches the site root with an empty root', () => {
    expect(getLatestPoll('', 'closed').request.path).toMatch(/^\/@search\?/);
  });

  it('keys open and closed searches apart', () => {
    expect(latestPollKey('', 'open')).not.toBe(latestPollKey('', 'closed'));
  });
});
