import React from 'react';
import { afterEach, describe, it, expect } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { Provider } from 'react-redux';
import { recordingStore } from '../testing/store';
import usePoll from './usePoll';
import { GET_POLL, VOTE_POLL } from '../constants/ActionTypes';
import open from '../__fixtures__/open.json';
import openAnonymous from '../__fixtures__/open-anonymous.json';
import openVoted from '../__fixtures__/open-voted.json';
import closed from '../__fixtures__/closed.json';

function entry(data: unknown) {
  return {
    loading: false,
    loaded: true,
    error: null,
    data,
    voting: false,
    voteError: null,
  };
}

function setup(path: string, data?: unknown, store?: any) {
  const theStore =
    store ?? recordingStore({ polls: data ? { [path]: entry(data) } : {} });
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <Provider store={theStore}>{children}</Provider>
  );
  return { store: theStore, ...renderHook(() => usePoll(path), { wrapper }) };
}

describe('usePoll', () => {
  afterEach(() => {
    document.cookie = `collective.poll.${openAnonymous.uid}=; max-age=0; path=/`;
  });

  it('fetches the poll after rendering', () => {
    const { store } = setup('/a-poll');
    expect(store.actions).toEqual([
      expect.objectContaining({ type: GET_POLL, path: '/a-poll' }),
    ]);
  });

  it('fetches nothing without a path', () => {
    const { store, result } = setup('');
    expect(store.actions).toEqual([]);
    expect(result.current.poll).toBeNull();
    expect(result.current.canVoteNow).toBe(false);
  });

  it('starts empty', () => {
    const { result } = setup('/a-poll');
    expect(result.current).toMatchObject({
      poll: null,
      loading: false,
      loaded: false,
      error: null,
      voting: false,
      voteError: null,
      hasVoted: false,
      canVoteNow: false,
    });
  });

  it('lets a member who has not voted vote', () => {
    const { result } = setup('/a-poll', open);
    expect(result.current.poll).toEqual(open);
    expect(result.current.hasVoted).toBe(false);
    expect(result.current.canVoteNow).toBe(true);
  });

  it('takes a member having voted from the backend', () => {
    const { result } = setup('/a-poll', openVoted);
    expect(result.current.hasVoted).toBe(true);
    expect(result.current.canVoteNow).toBe(false);
  });

  it('lets an anonymous visitor without the cookie vote', () => {
    const { result } = setup('/a-poll', openAnonymous);
    expect(result.current.hasVoted).toBe(false);
    expect(result.current.canVoteNow).toBe(true);
  });

  it('takes an anonymous visitor having voted from the cookie', () => {
    document.cookie = `collective.poll.${openAnonymous.uid}=xyz; path=/`;
    const { result } = setup('/a-poll', openAnonymous);
    expect(result.current.hasVoted).toBe(true);
    expect(result.current.canVoteNow).toBe(false);
  });

  it('does not offer a vote in a closed poll', () => {
    const { result } = setup('/a-poll', closed);
    expect(result.current.canVoteNow).toBe(false);
  });

  it('votes', async () => {
    const { store, result } = setup('/a-poll', open);
    await act(() => result.current.vote([1]));
    expect(store.actions).toContainEqual(
      expect.objectContaining({
        type: VOTE_POLL,
        path: '/a-poll',
        request: expect.objectContaining({ data: { option_ids: [1] } }),
      }),
    );
  });

  it('swallows a failed vote: the store holds the error', async () => {
    const store = recordingStore(
      { polls: { '/a-poll': entry(open) } },
      (action) =>
        action.type === VOTE_POLL ? Promise.reject(new Error('403')) : action,
    );
    const { result } = setup('/a-poll', undefined, store);
    await expect(act(() => result.current.vote([0]))).resolves.toBeUndefined();
  });
});
