import { describe, it, expect } from 'vitest';
import ResultsPie, { slicePath } from './ResultsPie';
import { RESULT_SETS, makeResults } from '../../testing/results';
import { renderInVolto } from '../../testing/render';

function drawn(container: HTMLElement) {
  return Array.from(container.querySelectorAll('svg [data-option]')).map(
    (el) => `${el.tagName.toLowerCase()}:${el.getAttribute('data-option')}`,
  );
}

describe('ResultsPie', () => {
  it('draws a slice for every option with votes', () => {
    const { container } = renderInVolto(
      <ResultsPie results={RESULT_SETS.several} />,
    );
    expect(drawn(container)).toEqual(['path:0', 'path:1', 'path:2']);
  });

  it('draws no slice for a zero option', () => {
    const { container } = renderInVolto(
      <ResultsPie results={RESULT_SETS.aZeroOption} />,
    );
    expect(drawn(container)).toEqual(['path:0', 'path:2']);
  });

  it('draws an empty circle with no votes', () => {
    const { container } = renderInVolto(
      <ResultsPie results={RESULT_SETS.allZero} />,
    );
    expect(drawn(container)).toEqual([]);
    expect(container.querySelector('.poll-results-pie__empty')).not.toBeNull();
    expect(container.textContent).not.toMatch(/NaN|undefined/);
  });

  it('draws a full circle for a single option with votes', () => {
    const { container } = renderInVolto(
      <ResultsPie results={RESULT_SETS.oneAtFull} />,
    );
    expect(drawn(container)).toEqual(['circle:1']);
  });

  it('carries the values as text in the legend', () => {
    const { container } = renderInVolto(
      <ResultsPie results={RESULT_SETS.several} />,
    );
    const legend = Array.from(
      container.querySelectorAll('.poll-results-pie__legend li'),
    ).map((li) => li.textContent);
    expect(legend).toEqual([
      'Option A: 5 (50%)',
      'Option B: 3 (30%)',
      'Option C: 2 (20%)',
    ]);
  });

  it('keeps a table for assistive technology', () => {
    const { getByRole, container } = renderInVolto(
      <ResultsPie results={makeResults(1, 1)} />,
    );
    expect(getByRole('table', { name: 'Poll results' })).toBeTruthy();
    expect(
      container
        .querySelector('.poll-results-pie__chart')
        ?.getAttribute('aria-hidden'),
    ).toBe('true');
  });
});

describe('slicePath', () => {
  it('uses the large arc flag past half the circle', () => {
    expect(slicePath(0, 0.75)).toContain(' 0 1 1 ');
    expect(slicePath(0, 0.25)).toContain(' 0 0 1 ');
  });

  it('starts at the top', () => {
    expect(slicePath(0, 0.25)).toMatch(/^M 50 50 L 50 0 /);
  });
});
