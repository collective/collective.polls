import { describe, it, expect } from 'vitest';
import type { ConfigType } from '@plone/registry';
import installSettings from './settings';

describe('installSettings', () => {
  it('returns the same registry, untouched', () => {
    const config = { settings: { a: 1 } } as unknown as ConfigType;
    expect(installSettings(config)).toBe(config);
    expect(config.settings).toEqual({ a: 1 });
  });
});
