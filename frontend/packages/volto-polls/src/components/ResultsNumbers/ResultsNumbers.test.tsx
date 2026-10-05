import { describe, it, expect } from 'vitest';
import { within } from '@testing-library/react';
import ResultsNumbers from './ResultsNumbers';
import { RESULT_SETS } from '../../testing/results';
import { renderInVolto } from '../../testing/render';

function rows(container: HTMLElement) {
  return Array.from(container.querySelectorAll('tbody tr')).map((tr) =>
    Array.from(tr.children).map((cell) => cell.textContent),
  );
}

describe('ResultsNumbers', () => {
  it('shows option, votes and percentage for every option', () => {
    const { container } = renderInVolto(
      <ResultsNumbers results={RESULT_SETS.several} />,
    );
    expect(rows(container)).toEqual([
      ['Option A', '5', '50%'],
      ['Option B', '3', '30%'],
      ['Option C', '2', '20%'],
    ]);
  });

  it('is a labelled table with column headers', () => {
    const { getByRole } = renderInVolto(
      <ResultsNumbers results={RESULT_SETS.several} />,
    );
    const table = getByRole('table', { name: 'Poll results' });
    expect(
      within(table)
        .getAllByRole('columnheader')
        .map((h) => h.textContent),
    ).toEqual(['Option', 'Votes', 'Percentage']);
  });

  it('shows a zero option as zero', () => {
    const { container } = renderInVolto(
      <ResultsNumbers results={RESULT_SETS.aZeroOption} />,
    );
    expect(rows(container)[1]).toEqual(['Option B', '0', '0%']);
  });

  it('shows zeros, not NaN, with no votes', () => {
    const { container } = renderInVolto(
      <ResultsNumbers results={RESULT_SETS.allZero} />,
    );
    expect(container.textContent).not.toMatch(/NaN|undefined/);
    expect(rows(container).map((r) => r[2])).toEqual(['0%', '0%', '0%']);
  });

  it('shows one option at 100%', () => {
    const { container } = renderInVolto(
      <ResultsNumbers results={RESULT_SETS.oneAtFull} />,
    );
    expect(rows(container)[1]).toEqual(['Option B', '7', '100%']);
  });

  it('can be visually hidden, as the twin of a chart', () => {
    const { container } = renderInVolto(
      <ResultsNumbers results={RESULT_SETS.several} visuallyHidden />,
    );
    expect(
      container
        .querySelector('table')
        ?.classList.contains('polls-visually-hidden'),
    ).toBe(true);
  });
});
