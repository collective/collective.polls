import type React from 'react';
import type { ConfigType } from '@plone/registry';
import Poll from '../components/Poll/Poll';
import { GRAPH_COMPONENT } from '../components/PollResults/PollResults';
import ResultsBar from '../components/ResultsBar/ResultsBar';
import ResultsNumbers from '../components/ResultsNumbers/ResultsNumbers';
import ResultsPie from '../components/ResultsPie/ResultsPie';
import { POLL_COMPONENT } from '../helpers/components';

/**
 * Register the components a project can replace.
 *
 * `Poll` displays a poll in the poll view and in the poll block alike.
 * `PollResultsGraph`, with the graph type as dependency, draws the results
 * of a poll whose `results_graph` is that type.
 *
 * @param config - The Volto configuration registry.
 * @returns The same registry.
 */
export default function install(config: ConfigType) {
  config.registerComponent({
    name: POLL_COMPONENT,
    component: Poll as unknown as React.ComponentType,
  });
  const graphs = { bar: ResultsBar, pie: ResultsPie, numbers: ResultsNumbers };
  for (const [graph, component] of Object.entries(graphs)) {
    config.registerComponent({
      name: GRAPH_COMPONENT,
      dependencies: [graph],
      component: component as unknown as React.ComponentType,
    });
  }
  return config;
}
