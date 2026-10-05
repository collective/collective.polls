import { describe, it, expect } from 'vitest';
import { latestPolls, polls, toPollError } from './polls';
import { GET_LATEST_POLL, GET_POLL, VOTE_POLL } from '../constants/ActionTypes';
import open from '../__fixtures__/open.json';
import openVoted from '../__fixtures__/open-voted.json';

describe('polls', () => {
  it('starts empty and ignores actions without a path', () => {
    expect(polls(undefined, { type: 'OTHER' })).toEqual({});
    expect(polls({}, { type: `${GET_POLL}_PENDING` })).toEqual({});
  });

  it('loads a poll', () => {
    let state = polls({}, { type: `${GET_POLL}_PENDING`, path: '/a' });
    expect(state['/a']).toMatchObject({ loading: true, loaded: false });
    state = polls(state, {
      type: `${GET_POLL}_SUCCESS`,
      path: '/a',
      result: open,
    });
    expect(state['/a']).toMatchObject({
      loading: false,
      loaded: true,
      data: open,
    });
  });

  it('keeps two polls on one page apart', () => {
    let state = polls(
      {},
      { type: `${GET_POLL}_SUCCESS`, path: '/a', result: open },
    );
    state = polls(state, {
      type: `${GET_POLL}_SUCCESS`,
      path: '/b',
      result: openVoted,
    });
    expect(state['/a'].data).toBe(open);
    expect(state['/b'].data).toBe(openVoted);
  });

  it('records a failed read', () => {
    const state = polls(
      {},
      {
        type: `${GET_POLL}_FAIL`,
        path: '/a',
        error: { status: 401, response: { body: { type: 'Unauthorized' } } },
      },
    );
    expect(state['/a']).toMatchObject({
      loading: false,
      loaded: false,
      error: { status: 401, type: 'Unauthorized' },
    });
  });

  it('replaces only its own poll after a vote', () => {
    let state = polls(
      {},
      { type: `${GET_POLL}_SUCCESS`, path: '/a', result: open },
    );
    state = polls(state, {
      type: `${GET_POLL}_SUCCESS`,
      path: '/b',
      result: open,
    });
    state = polls(state, { type: `${VOTE_POLL}_PENDING`, path: '/a' });
    expect(state['/a'].voting).toBe(true);
    state = polls(state, {
      type: `${VOTE_POLL}_SUCCESS`,
      path: '/a',
      result: openVoted,
    });
    expect(state['/a']).toMatchObject({ voting: false, data: openVoted });
    expect(state['/b'].data).toBe(open);
  });

  it('keeps the last state when a vote fails', () => {
    let state = polls(
      {},
      { type: `${GET_POLL}_SUCCESS`, path: '/a', result: open },
    );
    state = polls(state, {
      type: `${VOTE_POLL}_FAIL`,
      path: '/a',
      error: {
        status: 403,
        response: {
          body: {
            error: { type: 'AlreadyVoted', message: 'You already voted.' },
          },
        },
      },
    });
    expect(state['/a']).toMatchObject({
      voting: false,
      data: open,
      voteError: {
        status: 403,
        type: 'AlreadyVoted',
        message: 'You already voted.',
      },
    });
  });

  it('clears an earlier vote error on a new vote', () => {
    let state = polls(
      {},
      {
        type: `${VOTE_POLL}_FAIL`,
        path: '/a',
        error: { status: 400 },
      },
    );
    state = polls(state, { type: `${VOTE_POLL}_PENDING`, path: '/a' });
    expect(state['/a'].voteError).toBeNull();
  });

  it('ignores unrelated actions with a path', () => {
    const state = {};
    expect(polls(state, { type: 'OTHER', path: '/a' })).toBe(state);
  });
});

describe('latestPolls', () => {
  it('starts empty and ignores actions without a key', () => {
    expect(latestPolls(undefined, { type: 'OTHER' })).toEqual({});
  });

  it('records the path of the poll found', () => {
    let state = latestPolls(
      {},
      { type: `${GET_LATEST_POLL}_PENDING`, key: 'k' },
    );
    expect(state.k.loading).toBe(true);
    state = latestPolls(state, {
      type: `${GET_LATEST_POLL}_SUCCESS`,
      key: 'k',
      result: {
        items: [{ '@id': 'http://localhost:3000/a-poll', title: 'A poll' }],
      },
    });
    expect(state.k).toMatchObject({
      loading: false,
      loaded: true,
      path: 'http://localhost:3000/a-poll',
      title: 'A poll',
    });
  });

  it('records that nothing was found', () => {
    const state = latestPolls(
      {},
      {
        type: `${GET_LATEST_POLL}_SUCCESS`,
        key: 'k',
        result: { items: [] },
      },
    );
    expect(state.k).toMatchObject({ loaded: true, path: null, title: null });
  });

  it('treats a failed search as nothing found', () => {
    const state = latestPolls(
      {},
      {
        type: `${GET_LATEST_POLL}_FAIL`,
        key: 'k',
        error: { status: 500 },
      },
    );
    expect(state.k).toMatchObject({
      loaded: true,
      path: null,
      error: { status: 500 },
    });
  });

  it('ignores unrelated actions with a key', () => {
    const state = {};
    expect(latestPolls(state, { type: 'OTHER', key: 'k' })).toBe(state);
  });
});

describe('toPollError', () => {
  it('reads plone.rest bodies', () => {
    expect(
      toPollError({
        status: 401,
        response: { body: { type: 'Unauthorized', message: 'No.' } },
      }),
    ).toEqual({ status: 401, type: 'Unauthorized', message: 'No.' });
  });

  it('takes the status from the response when the error lacks it', () => {
    expect(toPollError({ response: { status: 502 } })).toEqual({
      status: 502,
      type: undefined,
      message: undefined,
    });
  });

  it('copes with nothing at all', () => {
    expect(toPollError(undefined)).toEqual({
      status: undefined,
      type: undefined,
      message: undefined,
    });
  });
});
