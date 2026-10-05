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
import './results-bar.scss';

export interface ResultsBarProps {
  /** The results, in option order. */
  results: PollResult[];
}

/**
 * The results as horizontal bars, one per option.
 *
 * The bars are drawn for sighted readers only; the same numbers follow in a
 * table for assistive technology.
 */
export const ResultsBar = ({ results }: ResultsBarProps) => {
  const intl = useIntl();
  const percents = wholePercents(results);
  return (
    <div className="poll-results-bar">
      <ul aria-hidden="true">
        {results.map((result, index) => (
          <li key={result.option_id} className="poll-results-bar__item">
            <span className="poll-results-bar__label">
              {result.description}
            </span>
            <span className="poll-results-bar__track">
              <span
                className="poll-results-bar__fill"
                style={{
                  width: `${percents[index]}%`,
                  backgroundColor: optionColor(index),
                }}
              />
            </span>
            <span className="poll-results-bar__value">
              {result.votes} ({formatPercent(percents[index], intl.locale)})
            </span>
          </li>
        ))}
      </ul>
      <ResultsNumbers results={results} visuallyHidden />
    </div>
  );
};

export default ResultsBar;
