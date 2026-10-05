import React, { useState } from 'react';
import { defineMessages, useIntl } from 'react-intl';
import UniversalLink from '@plone/volto/components/manage/UniversalLink/UniversalLink';
import PollForm from '../PollForm/PollForm';
import PollResults from '../PollResults/PollResults';
import PollStatus, { type PollStatusKind } from '../PollStatus/PollStatus';
import TotalVotes from '../TotalVotes/TotalVotes';
import usePoll from '../../hooks/usePoll';
import type { PollError, PollOption, PollState } from '../../types/poll';
import '../../theme/polls.scss';
import './poll.scss';

const messages = defineMessages({
  showResults: {
    id: 'Show partial results',
    defaultMessage: 'Show partial results',
  },
  vote: { id: 'Vote', defaultMessage: 'Vote' },
});

export interface PollProps {
  /** The poll's path, relative to the site. */
  path: string;
  /** The question, shown as a heading; the page title already says it in the poll's own view. */
  title?: string;
  /** A heading above the poll, as the 2.x portlet had. */
  header?: string;
  /** Show the number of votes so far, when the user may see results. */
  showTotal?: boolean;
  /** Link the question to the poll. */
  linkToPoll?: boolean;
  /** `false` shows the poll without letting anyone vote, as when editing a page. */
  interactive?: boolean;
  /** Options to show until the poll's state arrives, such as on the server. */
  fallbackOptions?: PollOption[];
}

/**
 * Which messages a poll shows.
 *
 * @param poll The poll's state.
 * @param hasVoted The user has voted, by the backend or the cookie.
 * @param justVoted The user voted on this page, and the vote went through.
 * @param voteError Why the last vote failed, if it did.
 */
export function statusKinds(
  poll: PollState,
  hasVoted: boolean,
  justVoted: boolean,
  voteError: PollError | null = null,
): PollStatusKind[] {
  const kinds: PollStatusKind[] = [];
  if (voteError) {
    kinds.push(
      voteError.type === 'AlreadyVoted' ? 'alreadyVoted' : 'voteFailed',
    );
  } else if (justVoted) {
    kinds.push('thanks');
  } else if (hasVoted && poll.state === 'open') {
    kinds.push('alreadyVoted');
  }
  if (poll.state === 'closed') kinds.push('closed');
  if (poll.state === 'private' || poll.state === 'pending')
    kinds.push('notOpen');
  if (poll.state === 'open' && !poll.can_vote && !hasVoted)
    kinds.push('notAllowed');
  if (poll.anonymous_blocked) kinds.push('anonymousBlocked');
  return kinds;
}

/**
 * A poll: the vote form while the user can vote, the results otherwise.
 *
 * It fetches the poll's state for the current user in the browser, so the
 * server renders only the question and, given `fallbackOptions`, the
 * options with the vote turned off.
 */
export const Poll = ({
  path,
  title,
  header,
  showTotal = false,
  linkToPoll = false,
  interactive = true,
  fallbackOptions,
}: PollProps) => {
  const intl = useIntl();
  const { poll, error, vote, voting, voteError, hasVoted, canVoteNow } =
    usePoll(path);
  const [justVoted, setJustVoted] = useState(false);
  const [peek, setPeek] = useState(false);

  const onVote = async (optionId: number) => {
    await vote(optionId);
    setJustVoted(true);
    setPeek(false);
  };

  const results = poll?.results ?? null;
  // Someone who could see the results before voting, such as a reviewer.
  const canPeek = Boolean(
    poll &&
      canVoteNow &&
      poll.has_voted === false &&
      results &&
      (poll.total_votes ?? 0) > 0,
  );
  const showForm = poll ? canVoteNow && !(canPeek && peek) : false;
  const showResults = Boolean(results) && (!canVoteNow || (canPeek && peek));
  const kinds: PollStatusKind[] = poll
    ? statusKinds(poll, hasVoted, justVoted, voteError)
    : error
      ? ['unavailable']
      : [];

  return (
    <div className="poll" data-state={poll?.state} aria-busy={!poll && !error}>
      {header && <h2 className="poll__header">{header}</h2>}
      {title && (
        <p className="poll__title">
          {linkToPoll ? (
            <UniversalLink href={path}>{title}</UniversalLink>
          ) : (
            title
          )}
        </p>
      )}
      <PollStatus kinds={kinds} />
      {showForm && poll && (
        <PollForm
          options={poll.options}
          onVote={onVote}
          submitting={voting}
          disabled={!interactive}
          legend={title}
        />
      )}
      {!poll && !error && fallbackOptions && fallbackOptions.length > 0 && (
        <PollForm
          options={fallbackOptions}
          onVote={() => undefined}
          disabled
          legend={title}
        />
      )}
      {showResults && poll && results && (
        <PollResults
          results={results}
          graph={poll.results_graph}
          closed={poll.state === 'closed'}
        />
      )}
      {canPeek && (
        <button
          type="button"
          className="poll__toggle"
          aria-pressed={peek}
          onClick={() => setPeek(!peek)}
        >
          {intl.formatMessage(peek ? messages.vote : messages.showResults)}
        </button>
      )}
      {showTotal && showResults && poll?.total_votes !== null && poll && (
        <TotalVotes total={poll.total_votes ?? 0} />
      )}
    </div>
  );
};

export default Poll;
