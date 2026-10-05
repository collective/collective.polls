import React from 'react';
import { defineMessages, useIntl } from 'react-intl';
import './total-votes.scss';

const messages = defineMessages({
  total: { id: 'Total votes:', defaultMessage: 'Total votes:' },
});

export interface TotalVotesProps {
  /** The number of votes so far. */
  total: number;
}

/** "Total votes: N". */
export const TotalVotes = ({ total }: TotalVotesProps) => {
  const intl = useIntl();
  return (
    <p className="poll-total-votes">
      {intl.formatMessage(messages.total)}{' '}
      <strong>{intl.formatNumber(total)}</strong>
    </p>
  );
};

export default TotalVotes;
