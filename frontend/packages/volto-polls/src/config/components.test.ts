import { describe, it, expect } from 'vitest';
import type { ConfigType } from '@plone/registry';
import installComponents from './components';
import Poll from '../components/Poll/Poll';
import ResultsBar from '../components/ResultsBar/ResultsBar';
import ResultsNumbers from '../components/ResultsNumbers/ResultsNumbers';
import ResultsPie from '../components/ResultsPie/ResultsPie';

/** A registry stub recording what is registered, by full name. */
function makeConfig() {
  const registered: Record<string, unknown> = {};
  const config = {
    registerComponent: ({
      name,
      dependencies = [],
      component,
    }: {
      name: string;
      dependencies?: string[];
      component: unknown;
    }) => {
      const deps = dependencies.join('+');
      registered[deps ? `${name}|${deps}` : name] = component;
    },
  } as unknown as ConfigType;
  return { config, registered };
}

describe('installComponents', () => {
  it('registers the poll and one graph per type, nothing else', () => {
    const { config, registered } = makeConfig();
    installComponents(config);
    expect(registered).toEqual({
      Poll,
      'PollResultsGraph|bar': ResultsBar,
      'PollResultsGraph|pie': ResultsPie,
      'PollResultsGraph|numbers': ResultsNumbers,
    });
  });
});
