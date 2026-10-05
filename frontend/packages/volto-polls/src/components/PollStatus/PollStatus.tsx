import React from 'react';
import { defineMessages, useIntl } from 'react-intl';
import './poll-status.scss';

const messages = defineMessages({
  thanks: {
    id: 'Thanks for your vote',
    defaultMessage: 'Thanks for your vote',
  },
  closed: {
    id: 'This poll is closed.',
    defaultMessage: 'This poll is closed.',
  },
  notOpen: {
    id: 'This poll is not open yet.',
    defaultMessage: 'This poll is not open yet.',
  },
  alreadyVoted: {
    id: 'You already voted in this poll.',
    defaultMessage: 'You already voted in this poll.',
  },
  notAllowed: {
    id: 'You are not authorized to vote',
    defaultMessage: 'You are not authorized to vote',
  },
  anonymousBlocked: {
    id: "Anonymous user won't be able to vote, you forgot to publish the parent folder, you must sent back the poll to private state, publish the parent folder and open the poll again",
    defaultMessage:
      "Anonymous user won't be able to vote, you forgot to publish the parent folder, you must sent back the poll to private state, publish the parent folder and open the poll again",
  },
  voteFailed: {
    id: 'Your vote could not be registered. Please try again.',
    defaultMessage: 'Your vote could not be registered. Please try again.',
  },
  unavailable: {
    id: 'Nothing to see here',
    defaultMessage: 'Nothing to see here',
  },
});

/** Every message a poll can show. */
export type PollStatusKind = keyof typeof messages;

const LEVELS: Record<PollStatusKind, 'info' | 'warning' | 'error'> = {
  thanks: 'info',
  closed: 'info',
  notOpen: 'info',
  alreadyVoted: 'info',
  notAllowed: 'info',
  anonymousBlocked: 'warning',
  voteFailed: 'error',
  unavailable: 'info',
};

export interface PollStatusProps {
  /** The messages to show, in order; none leaves the region empty. */
  kinds: PollStatusKind[];
}

/**
 * The messages of a poll, in a live region.
 *
 * The region is always rendered, even empty, so that screen readers
 * announce a message the moment one appears, such as after voting.
 */
export const PollStatus = ({ kinds }: PollStatusProps) => {
  const intl = useIntl();
  return (
    <div className="poll-status" role="status" aria-live="polite">
      {kinds.map((kind) => (
        <p
          key={kind}
          className={`poll-status__message poll-status__message--${LEVELS[kind]}`}
          data-kind={kind}
        >
          {intl.formatMessage(messages[kind])}
        </p>
      ))}
    </div>
  );
};

export default PollStatus;
