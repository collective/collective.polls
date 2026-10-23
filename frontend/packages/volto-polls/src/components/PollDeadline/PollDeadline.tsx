import React from 'react';
import { defineMessages, useIntl } from 'react-intl';
import './poll-deadline.scss';

const messages = defineMessages({
  closes: {
    id: 'Voting closes on {date}.',
    defaultMessage: 'Voting closes on {date}.',
  },
});

export interface PollDeadlineProps {
  /** When voting ends, as ISO 8601. */
  closeDate: string;
}

/** "Voting closes on <date>.", in the reader's language and timezone. */
export const PollDeadline = ({ closeDate }: PollDeadlineProps) => {
  const intl = useIntl();
  const date = (
    <time dateTime={closeDate}>
      {intl.formatDate(closeDate, { dateStyle: 'long', timeStyle: 'short' })}
    </time>
  );
  return (
    <p className="poll-deadline">
      {intl.formatMessage(messages.closes, { date })}
    </p>
  );
};

export default PollDeadline;
