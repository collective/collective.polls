import { afterEach, describe, it, expect } from 'vitest';
import { hasVotedCookie } from './cookie';

describe('hasVotedCookie', () => {
  afterEach(() => {
    document.cookie = 'collective.poll.abc=; max-age=0; path=/';
  });

  it('finds the cookie of the poll', () => {
    expect(hasVotedCookie('abc', 'a=1; collective.poll.abc=xyz; b=2')).toBe(
      true,
    );
  });

  it('ignores the cookie of another poll', () => {
    expect(hasVotedCookie('abc', 'collective.poll.def=xyz')).toBe(false);
  });

  it('ignores an empty cookie', () => {
    expect(hasVotedCookie('abc', 'collective.poll.abc=')).toBe(false);
  });

  it('keeps values holding an equals sign', () => {
    expect(hasVotedCookie('abc', 'collective.poll.abc=a=b')).toBe(true);
  });

  it('is false without cookies', () => {
    expect(hasVotedCookie('abc', '')).toBe(false);
  });

  it('reads document.cookie by default', () => {
    expect(hasVotedCookie('abc')).toBe(false);
    document.cookie = 'collective.poll.abc=xyz; path=/';
    expect(hasVotedCookie('abc')).toBe(true);
  });
});
