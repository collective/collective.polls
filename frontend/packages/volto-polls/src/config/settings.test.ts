import { describe, it, expect } from 'vitest';
import type { ConfigType } from '@plone/registry';
import installSettings, { POLL_TYPE } from './settings';
import pollSVG from '../icons/poll.svg';

function makeConfig() {
  return {
    settings: { a: 1, contentIcons: { Document: 'page' } },
  } as unknown as ConfigType;
}

describe('installSettings', () => {
  it('returns the same registry', () => {
    const config = makeConfig();
    expect(installSettings(config)).toBe(config);
  });

  it('gives polls their icon', () => {
    const config = installSettings(makeConfig());
    expect(POLL_TYPE).toBe('collective.polls.poll');
    expect(config.settings.contentIcons[POLL_TYPE]).toBe(pollSVG);
    expect(pollSVG).toBeTruthy();
  });

  it('keeps the other settings and icons', () => {
    const config = installSettings(makeConfig());
    expect((config.settings as any).a).toBe(1);
    expect(config.settings.contentIcons.Document).toBe('page');
  });
});
