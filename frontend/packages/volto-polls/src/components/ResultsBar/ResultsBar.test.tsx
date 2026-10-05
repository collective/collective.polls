import { describe, it, expect } from 'vitest';
import ResultsBar from './ResultsBar';
import { RESULT_SETS } from '../../testing/results';
import { renderInVolto } from '../../testing/render';

function bars(container: HTMLElement) {
  return Array.from(
    container.querySelectorAll<HTMLElement>('.poll-results-bar__fill'),
  ).map((el) => el.style.width);
}

describe('ResultsBar', () => {
  it('draws one bar per option, sized by share', () => {
    const { container } = renderInVolto(
      <ResultsBar results={RESULT_SETS.several} />,
    );
    expect(bars(container)).toEqual(['50%', '30%', '20%']);
  });

  it('labels each bar with its option, votes and percentage', () => {
    const { container } = renderInVolto(
      <ResultsBar results={RESULT_SETS.several} />,
    );
    const item = container.querySelector('.poll-results-bar__item');
    expect(item?.textContent).toBe('Option A5 (50%)');
  });

  it('draws an empty bar for a zero option', () => {
    const { container } = renderInVolto(
      <ResultsBar results={RESULT_SETS.aZeroOption} />,
    );
    expect(bars(container)).toEqual(['80%', '0%', '20%']);
  });

  it('draws empty bars, not NaN, with no votes', () => {
    const { container } = renderInVolto(
      <ResultsBar results={RESULT_SETS.allZero} />,
    );
    expect(bars(container)).toEqual(['0%', '0%', '0%']);
    expect(container.textContent).not.toMatch(/NaN|undefined/);
  });

  it('fills one bar at 100%', () => {
    const { container } = renderInVolto(
      <ResultsBar results={RESULT_SETS.oneAtFull} />,
    );
    expect(bars(container)).toEqual(['0%', '100%', '0%']);
  });

  it('hides the drawing and keeps a table for assistive technology', () => {
    const { container, getByRole } = renderInVolto(
      <ResultsBar results={RESULT_SETS.several} />,
    );
    expect(container.querySelector('ul')?.getAttribute('aria-hidden')).toBe(
      'true',
    );
    expect(getByRole('table', { name: 'Poll results' })).toBeTruthy();
  });
});
