import { afterEach, describe, it, expect } from 'vitest';
import config from '@plone/volto/registry';
import { POLL_COMPONENT, locatePoll } from './components';
import Poll from '../components/Poll/Poll';

describe('locatePoll', () => {
  afterEach(() => {
    delete (config as any)._data.components[POLL_COMPONENT];
  });

  it('uses the add-on component when nothing is registered', () => {
    expect(locatePoll()).toBe(Poll);
  });

  it('uses the registered component', () => {
    const Custom = () => null;
    config.registerComponent({ name: POLL_COMPONENT, component: Custom });
    expect(locatePoll()).toBe(Custom);
  });
});
