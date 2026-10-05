import React from 'react';
import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { Provider } from 'react-redux';
import { recordingStore } from '../testing/store';
import useLatestPoll from './useLatestPoll';
import { GET_LATEST_POLL } from '../constants/ActionTypes';

function found(path: string | null, title: string | null = null) {
  return { loading: false, loaded: true, error: null, path, title };
}

function setup(
  latestPolls: Record<string, unknown>,
  includeClosed = false,
  enabled = true,
) {
  const store = recordingStore({ latestPolls });
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    // Only what react-redux reads; see testing/store.ts.
    <Provider store={store as any}>{children}</Provider>
  );
  const hook = renderHook(() => useLatestPoll('', includeClosed, enabled), {
    wrapper,
  });
  const keys = store.actions
    .filter((a: { type: string }) => a.type === GET_LATEST_POLL)
    .map((a: { key: string }) => a.key);
  return { result: hook.result, keys };
}

describe('useLatestPoll', () => {
  it('searches for the newest open poll', () => {
    const { result, keys } = setup({});
    expect(keys).toEqual(['|open']);
    expect(result.current).toEqual({ path: null, title: null, loaded: false });
  });

  it('answers the open poll found', () => {
    const { result, keys } = setup(
      { '|open': found('http://localhost:8080/Plone/a-poll', 'A poll') },
      true,
    );
    expect(result.current).toEqual({
      path: '/a-poll',
      title: 'A poll',
      loaded: true,
    });
    expect(keys).toEqual(['|open']);
  });

  it('answers nothing when no poll is open and closed ones are not wanted', () => {
    const { result, keys } = setup({ '|open': found(null) });
    expect(result.current).toEqual({ path: null, title: null, loaded: true });
    expect(keys).toEqual(['|open']);
  });

  it('falls back to the newest closed poll', () => {
    const { result, keys } = setup(
      { '|open': found(null), '|closed': found('/old-poll', 'Old poll') },
      true,
    );
    expect(keys).toEqual(['|open', '|closed']);
    expect(result.current).toEqual({
      path: '/old-poll',
      title: 'Old poll',
      loaded: true,
    });
  });

  it('waits for the closed search', () => {
    const { result } = setup({ '|open': found(null) }, true);
    expect(result.current).toEqual({ path: null, title: null, loaded: false });
  });

  it('answers nothing when nothing is closed either', () => {
    const { result } = setup(
      { '|open': found(null), '|closed': found(null) },
      true,
    );
    expect(result.current).toEqual({ path: null, title: null, loaded: true });
  });

  it('does not search when disabled', () => {
    const { result, keys } = setup({}, true, false);
    expect(keys).toEqual([]);
    expect(result.current).toEqual({ path: null, title: null, loaded: true });
  });
});
