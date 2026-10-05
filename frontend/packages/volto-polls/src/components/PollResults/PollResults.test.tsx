import React from 'react';
import { afterEach, describe, it, expect } from 'vitest';
import config from '@plone/volto/registry';
import PollResults, { GRAPH_COMPONENT, graphComponent } from './PollResults';
import ResultsBar from '../ResultsBar/ResultsBar';
import ResultsNumbers from '../ResultsNumbers/ResultsNumbers';
import ResultsPie from '../ResultsPie/ResultsPie';
import { RESULT_SETS } from '../../testing/results';
import { renderInVolto } from '../../testing/render';

const GRAPHS: [string, string][] = [
  ['bar', '.poll-results-bar'],
  ['pie', '.poll-results-pie'],
  ['numbers', 'table.poll-results-numbers:not(.polls-visually-hidden)'],
];

describe('PollResults', () => {
  afterEach(() => {
    delete (config as any)._data.components[`${GRAPH_COMPONENT}|bar`];
  });

  describe.each(GRAPHS)('%s', (graph, selector) => {
    it.each([
      [false, 'Partial results'],
      [true, 'Results'],
    ])('closed=%s is headed "%s"', (closed, heading) => {
      const { container, getByRole } = renderInVolto(
        <PollResults
          results={RESULT_SETS.several}
          graph={graph}
          closed={closed}
        />,
      );
      expect(getByRole('heading').textContent).toBe(heading);
      expect(container.querySelector(selector)).not.toBeNull();
    });
  });

  it('falls back to numbers for a graph it does not know', () => {
    expect(graphComponent('radar')).toBe(ResultsNumbers);
  });

  it('uses the built-in charts when nothing is registered', () => {
    expect(graphComponent('bar')).toBe(ResultsBar);
    expect(graphComponent('pie')).toBe(ResultsPie);
  });

  it('uses a chart registered for the graph type', () => {
    const Custom = () => <div className="custom-chart" />;
    config.registerComponent({
      name: GRAPH_COMPONENT,
      dependencies: ['bar'],
      component: Custom,
    });
    const { container } = renderInVolto(
      <PollResults results={RESULT_SETS.several} graph="bar" />,
    );
    expect(container.querySelector('.custom-chart')).not.toBeNull();
    expect(container.querySelector('.poll-results-bar')).toBeNull();
  });
});
