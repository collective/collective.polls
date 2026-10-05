import React from 'react';
import { useIntl } from 'react-intl';
import ResultsNumbers from '../ResultsNumbers/ResultsNumbers';
import {
  formatPercent,
  optionColor,
  wholePercents,
} from '../../helpers/results';
import type { PollResult } from '../../types/poll';
import '../../theme/polls.scss';
import './results-pie.scss';

export interface ResultsPieProps {
  /** The results, in option order. */
  results: PollResult[];
}

const SIZE = 100;
const R = SIZE / 2;

/** A point on the circle, `fraction` of the way round from the top. */
function point(fraction: number): [number, number] {
  const angle = 2 * Math.PI * fraction - Math.PI / 2;
  return [R + R * Math.cos(angle), R + R * Math.sin(angle)];
}

/** The SVG path of a slice from `start` to `end`, as fractions. */
export function slicePath(start: number, end: number): string {
  const [x1, y1] = point(start);
  const [x2, y2] = point(end);
  const large = end - start > 0.5 ? 1 : 0;
  return `M ${R} ${R} L ${x1} ${y1} A ${R} ${R} 0 ${large} 1 ${x2} ${y2} Z`;
}

/**
 * The results as a pie chart with a legend.
 *
 * The chart is drawn for sighted readers only; the same numbers follow in a
 * table for assistive technology. The legend carries the values as text, so
 * color is never the only way to tell options apart.
 */
export const ResultsPie = ({ results }: ResultsPieProps) => {
  const intl = useIntl();
  const percents = wholePercents(results);
  const total = results.reduce((sum, r) => sum + r.votes, 0);
  let start = 0;
  const slices = results.map((result, index) => {
    const fraction = total ? result.votes / total : 0;
    const slice = { index, start, end: start + fraction, fraction };
    start += fraction;
    return slice;
  });
  const full = slices.find((s) => s.fraction === 1);
  return (
    <div className="poll-results-pie">
      <div aria-hidden="true" className="poll-results-pie__chart">
        <svg viewBox={`0 0 ${SIZE} ${SIZE}`} role="presentation">
          {total === 0 && (
            <circle cx={R} cy={R} r={R} className="poll-results-pie__empty" />
          )}
          {full && (
            <circle
              cx={R}
              cy={R}
              r={R}
              fill={optionColor(full.index)}
              data-option={full.index}
            />
          )}
          {!full &&
            slices
              .filter((s) => s.fraction > 0)
              .map((s) => (
                <path
                  key={s.index}
                  d={slicePath(s.start, s.end)}
                  fill={optionColor(s.index)}
                  data-option={s.index}
                />
              ))}
        </svg>
        <ul className="poll-results-pie__legend">
          {results.map((result, index) => (
            <li key={result.option_id}>
              <span
                className="poll-results-pie__swatch"
                style={{ backgroundColor: optionColor(index) }}
              />
              {result.description}: {result.votes} (
              {formatPercent(percents[index], intl.locale)})
            </li>
          ))}
        </ul>
      </div>
      <ResultsNumbers results={results} visuallyHidden />
    </div>
  );
};

export default ResultsPie;
