import { describe, it, expect } from 'vitest';
import type { ConfigType } from '@plone/registry';
import installReducers from './reducers';
import { latestPolls, polls } from '../reducers/polls';

describe('installReducers', () => {
  it('registers both reducers', () => {
    const config = installReducers({
      addonReducers: {},
    } as unknown as ConfigType);
    expect(config.addonReducers?.polls).toBe(polls);
    expect(config.addonReducers?.latestPolls).toBe(latestPolls);
  });

  it('keeps reducers other add-ons registered', () => {
    const other = () => ({});
    const config = installReducers({
      addonReducers: { other },
    } as unknown as ConfigType);
    expect(config.addonReducers?.other).toBe(other);
  });

  it('survives a registry without add-on reducers', () => {
    const config = installReducers({} as unknown as ConfigType);
    expect(config.addonReducers?.polls).toBe(polls);
  });
});
