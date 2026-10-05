import React from 'react';
import { defineMessages, useIntl } from 'react-intl';
import config from '@plone/volto/registry';
import ResultsBar from '../ResultsBar/ResultsBar';
import ResultsNumbers from '../ResultsNumbers/ResultsNumbers';
import ResultsPie from '../ResultsPie/ResultsPie';
import type { PollResult, ResultsGraph } from '../../types/poll';
import './poll-results.scss';

const messages = defineMessages({
  partial: { id: 'Partial results', defaultMessage: 'Partial results' },
  final: { id: 'Results', defaultMessage: 'Results' },
});

/** The name graph components are registered under, one per graph type. */
export const GRAPH_COMPONENT = 'PollResultsGraph';

/** What ships with the add-on, used when nothing is registered. */
const BUILT_IN: Record<
  string,
  React.ComponentType<{ results: PollResult[] }>
> = {
  bar: ResultsBar,
  pie: ResultsPie,
  numbers: ResultsNumbers,
};

/**
 * Find the component that draws a graph type.
 *
 * Looked up in the registry as `PollResultsGraph` with the graph type as
 * dependency, so a project can replace a chart, or add a graph type the
 * backend offers, without touching this add-on.
 *
 * @param graph The poll's `results_graph`.
 */
export function graphComponent(
  graph: ResultsGraph | string,
): React.ComponentType<{ results: PollResult[] }> {
  const registered = config.getComponent?.({
    name: GRAPH_COMPONENT,
    dependencies: [graph],
  })?.component as React.ComponentType<{ results: PollResult[] }> | undefined;
  return registered ?? BUILT_IN[graph] ?? ResultsNumbers;
}

export interface PollResultsProps {
  /** The results, in option order. */
  results: PollResult[];
  /** The poll's `results_graph`. */
  graph: ResultsGraph | string;
  /** The poll is closed: these are its final results. */
  closed?: boolean;
}

/** The results of a poll, drawn the way the poll asks for. */
export const PollResults = ({
  results,
  graph,
  closed = false,
}: PollResultsProps) => {
  const intl = useIntl();
  const Graph = graphComponent(graph);
  return (
    <section className={`poll-results poll-results--${graph}`}>
      <h3 className="poll-results__heading">
        {intl.formatMessage(closed ? messages.final : messages.partial)}
      </h3>
      <Graph results={results} />
    </section>
  );
};

export default PollResults;
