import React from 'react';
import { defineMessages, useIntl } from 'react-intl';
import { formatPercent, wholePercents } from '../../helpers/results';
import type { PollResult } from '../../types/poll';
import '../../theme/polls.scss';
import './results-numbers.scss';

const messages = defineMessages({
  caption: { id: 'Poll results', defaultMessage: 'Poll results' },
  option: { id: 'Option', defaultMessage: 'Option' },
  votes: { id: 'Votes', defaultMessage: 'Votes' },
  percentage: { id: 'Percentage', defaultMessage: 'Percentage' },
});

export interface ResultsNumbersProps {
  /** The results, in option order. */
  results: PollResult[];
  /** Keep the table for assistive technology only, as charts do. */
  visuallyHidden?: boolean;
}

/**
 * The results as a table: option, votes and percentage.
 *
 * It is the "numbers" graph, and the accessible twin of the charts.
 */
export const ResultsNumbers = ({
  results,
  visuallyHidden = false,
}: ResultsNumbersProps) => {
  const intl = useIntl();
  const percents = wholePercents(results);
  const classes = ['poll-results-numbers'];
  if (visuallyHidden) classes.push('polls-visually-hidden');
  return (
    <table className={classes.join(' ')}>
      <caption className="polls-visually-hidden">
        {intl.formatMessage(messages.caption)}
      </caption>
      <thead>
        <tr>
          <th scope="col">{intl.formatMessage(messages.option)}</th>
          <th scope="col">{intl.formatMessage(messages.votes)}</th>
          <th scope="col">{intl.formatMessage(messages.percentage)}</th>
        </tr>
      </thead>
      <tbody>
        {results.map((result, index) => (
          <tr key={result.option_id}>
            <th scope="row">{result.description}</th>
            <td>{result.votes}</td>
            <td>{formatPercent(percents[index], intl.locale)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ResultsNumbers;
