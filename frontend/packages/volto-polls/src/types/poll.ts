/**
 * Types of the poll API, mirroring what the backend answers.
 *
 * `PollState` is the payload of `GET @poll` and `POST @vote`; the JSON
 * Schema the backend tests every response against is
 * `backend/tests/_resources/poll.schema.json`.
 */
import type { Content } from '@plone/types';

/** The workflow states of a poll. */
export type PollWorkflowState = 'private' | 'pending' | 'open' | 'closed';

/** How a poll shows its results. */
export type ResultsGraph = 'bar' | 'pie' | 'numbers';

/** One option of a poll. */
export interface PollOption {
  /** Stable id; votes are counted by it. Missing only before saving. */
  option_id: number;
  description: string;
}

/** The votes for one option. */
export interface PollResult extends PollOption {
  votes: number;
  /** Share of the votes, a fraction in `[0, 1]`; `0` with no votes. */
  percentage: number;
}

/** The state of a poll as seen by the current user. */
export interface PollState {
  '@id': string;
  uid: string;
  state: PollWorkflowState;
  allow_anonymous: boolean;
  /** Open, meant for anonymous votes, but anonymous visitors cannot vote. */
  anonymous_blocked: boolean;
  show_results: boolean;
  results_graph: ResultsGraph;
  options: PollOption[];
  /** The caller holds the vote permission. Says nothing about having voted. */
  can_vote: boolean;
  /** `null` for anonymous callers: the browser answers from the cookie. */
  has_voted: boolean | null;
  /** `null` when the caller may not see results. */
  total_votes: number | null;
  results: PollResult[] | null;
}

/** A term of a choice field, as plone.restapi serializes it. */
export interface Term {
  token: string;
  title: string | null;
}

/** A poll as the content API serializes it. */
export interface PollContent extends Content {
  '@type': 'collective.polls.poll';
  options: PollOption[];
  allow_anonymous: boolean;
  show_results: boolean;
  results_graph: Term | ResultsGraph | null;
}

/** An object browser selection. */
export interface PollHref {
  '@id': string;
  title?: string;
  Title?: string;
}

/** The settings of a poll block: the 2.x portlet's fields. */
export interface PollBlockData {
  '@type'?: 'poll';
  /** Show the newest open poll, or a chosen one. */
  mode?: 'latest' | 'chosen';
  poll?: PollHref[];
  header?: string;
  show_total?: boolean;
  /** With no open poll to show, show the newest closed one instead. */
  show_closed?: boolean;
  link_poll?: boolean;
}

/** Why a request about a poll failed. */
export interface PollError {
  /** HTTP status, when there was a response. */
  status?: number;
  /** The `type` of the error body, such as `AlreadyVoted`. */
  type?: string;
  message?: string;
}

/** What the store keeps for one poll. */
export interface PollEntry {
  loading: boolean;
  loaded: boolean;
  error: PollError | null;
  data: PollState | null;
  voting: boolean;
  voteError: PollError | null;
}

/** The newest poll found by a search. */
export interface LatestPollEntry {
  loading: boolean;
  loaded: boolean;
  error: PollError | null;
  /** Path of the poll found, `null` when there is none. */
  path: string | null;
  /** Title of the poll found. */
  title: string | null;
}

/** The add-on's slice of the Redux store. */
export interface PollsStoreState {
  polls: Record<string, PollEntry>;
  latestPolls: Record<string, LatestPollEntry>;
}
