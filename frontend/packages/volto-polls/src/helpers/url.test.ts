import { describe, it, expect } from 'vitest';
import { pollPath } from './url';

describe('pollPath', () => {
  it.each([
    ['http://localhost:8080/Plone/a-poll', '/a-poll'],
    ['http://localhost:8080/Plone/a-poll/@poll', '/a-poll'],
    ['http://localhost:8080/Plone/folder/a-poll/', '/folder/a-poll'],
    ['/a-poll', '/a-poll'],
  ])('%s → %s', (url, expected) => {
    expect(pollPath(url)).toBe(expected);
  });
});
