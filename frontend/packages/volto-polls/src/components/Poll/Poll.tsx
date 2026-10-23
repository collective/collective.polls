import React, { useState } from 'react';
import { defineMessages, useIntl } from 'react-intl';
import UniversalLink from '@plone/volto/components/manage/UniversalLink/UniversalLink';
import PollDeadline from '../PollDeadline/PollDeadline';
import PollForm from '../PollForm/PollForm';
import PollResults from '../PollResults/PollResults';
import PollStatus, { type PollStatusKind } from '../PollStatus/PollStatus';
import TotalVotes from '../TotalVotes/TotalVotes';
import { resultsAllowed } from '../../helpers/results';
import useOptionOrder from '../../hooks/useOptionOrder';
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
  /** How many options a voter can pick, until the poll's state arrives. */
  fallbackMaxChoices?: number;
  /** The legend above the options, until the poll's state arrives. */
  fallbackLegend?: string | null;
  /**
   * `results` shows only the results, once the user may see them, and says
   * when they will show otherwise; the vote happens elsewhere.
   */
  display?: 'poll' | 'results';
}

/**
 * Whether voting in a poll has ended: it is closed, or past its closing date.
 *
 * @param poll The poll's state.
 */
export function votingEnded(poll: PollState): boolean {
  return poll.state === 'closed' || (poll.state === 'open' && poll.expired);
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
  // A vote refused because the closing date passed after the poll was
  // fetched: the poll is closed, which says it all.
  const refusedAsClosed = voteError?.type === 'PollClosed';
  const ended = votingEnded(poll) || refusedAsClosed;
  if (voteError) {
    if (!refusedAsClosed)
      kinds.push(
        voteError.type === 'AlreadyVoted' ? 'alreadyVoted' : 'voteFailed',
      );
  } else if (justVoted) {
    kinds.push('thanks');
  } else if (hasVoted && !ended && poll.state === 'open') {
    kinds.push('alreadyVoted');
  }
  if (ended) kinds.push('closed');
  if (poll.state === 'private' || poll.state === 'pending')
    kinds.push('notOpen');
  if (poll.state === 'open' && !ended && !poll.can_vote && !hasVoted)
    kinds.push('notAllowed');
  if (poll.anonymous_blocked) kinds.push('anonymousBlocked');
  return kinds;
}

/**
 * Which messages a poll shows when it displays only its results.
 *
 * @param poll The poll's state.
 * @param shown The results are on display.
 */
export function resultsStatusKinds(
  poll: PollState,
  shown: boolean,
): PollStatusKind[] {
  if (votingEnded(poll)) return ['closed'];
  if (poll.state === 'private' || poll.state === 'pending') return ['notOpen'];
  if (shown) return [];
  return [
    poll.show_results === 'after_vote'
      ? 'resultsAfterVote'
      : 'resultsWhenClosed',
  ];
}

/**
 * A poll: the vote form while the user can vote, only the options while
 * the poll is not open yet, the results otherwise. With `display` set to
 * `results`, only the results.
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
  fallbackMaxChoices,
  fallbackLegend,
  display = 'poll',
}: PollProps) => {
  const intl = useIntl();
  const {
    poll,
    error,
    vote,
    voting,
    voteError,
    hasVoted,
    canVoteNow: canVote,
  } = usePoll(path);
  // The closing date passed after the poll was fetched.
  const canVoteNow = canVote && voteError?.type !== 'PollClosed';
  const [justVoted, setJustVoted] = useState(false);
  const [peek, setPeek] = useState(false);
  // Shuffled once here, not in the form: showing the results and coming
  // back to the vote must not move the options again.
  const options = useOptionOrder(
    poll?.options ?? [],
    Boolean(poll?.shuffle_options),
  );

  const onVote = async (optionIds: number[]) => {
    await vote(optionIds);
    setJustVoted(true);
    setPeek(false);
  };

  const resultsOnly = display === 'results';
  const results = poll?.results ?? null;
  // Not open yet: show what will be asked, not results nobody voted for.
  const notOpen = poll?.state === 'private' || poll?.state === 'pending';
  const allowed = Boolean(poll && !notOpen && resultsAllowed(poll, canVoteNow));
  // Someone who may see the results before voting: a reviewer, or anyone
  // when the poll always shows them.
  const canPeek =
    !resultsOnly && allowed && canVoteNow && (poll?.total_votes ?? 0) > 0;
  const showForm =
    poll && !resultsOnly ? canVoteNow && !(canPeek && peek) : false;
  const showResults =
    allowed && (resultsOnly || !canVoteNow || (canPeek && peek));
  const kinds: PollStatusKind[] = poll
    ? resultsOnly
      ? resultsStatusKinds(poll, showResults)
      : statusKinds(poll, hasVoted, justVoted, voteError)
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
      {poll?.close_date && !poll.expired && poll.state !== 'closed' && (
        <PollDeadline closeDate={poll.close_date} />
      )}
      {showForm && poll && (
        <PollForm
          options={options}
          onVote={onVote}
          maxChoices={poll.max_choices}
          submitting={voting}
          disabled={!interactive}
          legend={poll.legend}
        />
      )}
      {notOpen && poll && !resultsOnly && (
        <PollForm
          options={options}
          onVote={() => undefined}
          maxChoices={poll.max_choices}
          readOnly
          legend={poll.legend}
        />
      )}
      {!poll &&
        !error &&
        !resultsOnly &&
        fallbackOptions &&
        fallbackOptions.length > 0 && (
          <PollForm
            options={fallbackOptions}
            onVote={() => undefined}
            maxChoices={fallbackMaxChoices}
            disabled
            legend={fallbackLegend}
          />
        )}
      {showResults && poll && results && (
        <PollResults
          results={results}
          graph={poll.results_graph}
          closed={votingEnded(poll)}
          multipleChoice={poll.max_choices > 1}
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
