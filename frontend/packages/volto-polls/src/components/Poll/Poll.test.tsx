import React from 'react';
import { afterEach, describe, it, expect, vi } from 'vitest';
import { act, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import Poll, { statusKinds } from './Poll';
import { recordingStore } from '../../testing/store';
import { renderInVolto } from '../../testing/render';
import { VOTE_POLL } from '../../constants/ActionTypes';
import type { PollError, PollState } from '../../types/poll';
import closed from '../../__fixtures__/closed.json';
import noVotes from '../../__fixtures__/no-votes.json';
import open from '../../__fixtures__/open.json';
import multiple from '../../__fixtures__/open-multiple.json';
import openAnonymous from '../../__fixtures__/open-anonymous.json';
import openAnonymousBlocked from '../../__fixtures__/open-anonymous-blocked.json';
import openVoted from '../../__fixtures__/open-voted.json';
import openVotedHidden from '../../__fixtures__/open-voted-hidden-results.json';
import privatePoll from '../../__fixtures__/private.json';

const PATH = '/a-poll';

function entry(data: unknown, changes: Record<string, unknown> = {}) {
  return {
    loading: false,
    loaded: Boolean(data),
    error: null,
    data,
    voting: false,
    voteError: null,
    ...changes,
  };
}

function setup(
  props: Partial<React.ComponentProps<typeof Poll>> = {},
  pollEntry?: Record<string, unknown>,
  dispatch?: (action: any) => any,
) {
  const store = recordingStore(
    { polls: pollEntry ? { [PATH]: pollEntry } : {}, userSession: {} },
    dispatch,
  );
  const utils = renderInVolto(
    <Provider store={store as any}>
      <Poll path={PATH} {...props} />
    </Provider>,
  );
  const kinds = () =>
    Array.from(utils.container.querySelectorAll('[data-kind]')).map((el) =>
      el.getAttribute('data-kind'),
    );
  const form = () => utils.container.querySelector('form.poll-form');
  const results = () => utils.container.querySelector('.poll-results');
  return { store, kinds, form, results, ...utils };
}

describe('Poll', () => {
  afterEach(() => {
    document.cookie = `collective.poll.${openAnonymous.uid}=; max-age=0; path=/`;
  });

  it('offers the vote to a member who has not voted', () => {
    const { form, results, kinds } = setup({}, entry(open));
    expect(form()).not.toBeNull();
    expect(results()).toBeNull();
    expect(kinds()).toEqual([]);
  });

  it('shows a member who voted the results', () => {
    const { form, results, kinds, getByRole } = setup({}, entry(openVoted));
    expect(form()).toBeNull();
    expect(results()).not.toBeNull();
    expect(getByRole('heading', { name: 'Partial results' })).toBeTruthy();
    expect(kinds()).toEqual(['alreadyVoted']);
  });

  it('shows a member who voted nothing when results are hidden', () => {
    const { form, results, kinds } = setup({}, entry(openVotedHidden));
    expect(form()).toBeNull();
    expect(results()).toBeNull();
    expect(kinds()).toEqual(['alreadyVoted']);
  });

  it('offers the vote to an anonymous visitor without the cookie', () => {
    const { form, results } = setup({}, entry(openAnonymous));
    expect(form()).not.toBeNull();
    expect(results()).toBeNull();
  });

  it('shows an anonymous visitor with the cookie the results', () => {
    document.cookie = `collective.poll.${openAnonymous.uid}=xyz; path=/`;
    const { form, results, kinds } = setup({}, entry(openAnonymous));
    expect(form()).toBeNull();
    expect(results()).not.toBeNull();
    expect(kinds()).toEqual(['alreadyVoted']);
  });

  it('shows the final results of a closed poll', () => {
    const { form, getByRole, kinds } = setup({}, entry(closed));
    expect(form()).toBeNull();
    expect(getByRole('heading', { name: 'Results' })).toBeTruthy();
    expect(kinds()).toEqual(['closed']);
  });

  it('shows the options of a private poll, without results or vote', () => {
    const { form, results, kinds, getAllByRole, queryByRole } = setup(
      {},
      entry(privatePoll),
    );
    expect(form()).not.toBeNull();
    expect(getAllByRole('radio').every((r) => r.matches(':disabled'))).toBe(
      true,
    );
    expect(queryByRole('button', { name: 'Vote' })).toBeNull();
    expect(results()).toBeNull();
    expect(kinds()).toEqual(['notOpen']);
  });

  it('shows the options of a pending poll, without results or vote', () => {
    const { form, results, kinds, queryByRole } = setup(
      { showTotal: true },
      entry({ ...privatePoll, state: 'pending' }),
    );
    expect(form()).not.toBeNull();
    expect(queryByRole('button', { name: 'Vote' })).toBeNull();
    expect(results()).toBeNull();
    expect(kinds()).toEqual(['notOpen']);
  });

  it('warns that anonymous visitors cannot vote', () => {
    const { kinds } = setup({}, entry(openAnonymousBlocked));
    expect(kinds()).toEqual(['anonymousBlocked']);
  });

  it('lets a reviewer look at the results before voting', () => {
    const data = { ...openVoted, has_voted: false };
    const { form, results, getByRole } = setup({}, entry(data));
    expect(form()).not.toBeNull();
    const toggle = getByRole('button', { name: 'Show partial results' });
    expect(toggle.getAttribute('aria-pressed')).toBe('false');
    fireEvent.click(toggle);
    expect(form()).toBeNull();
    expect(results()).not.toBeNull();
    fireEvent.click(getByRole('button', { name: 'Vote' }));
    expect(form()).not.toBeNull();
  });

  it('offers no peek at a poll without votes', () => {
    const data = { ...noVotes, has_voted: false };
    const { queryByRole } = setup({}, entry(data));
    expect(queryByRole('button', { name: 'Show partial results' })).toBeNull();
  });

  it('votes, then thanks', async () => {
    const { store, getByRole, kinds } = setup({}, entry(open), (action) =>
      action.type === VOTE_POLL ? Promise.resolve(openVoted) : action,
    );
    fireEvent.click(getByRole('radio', { name: 'No' }));
    await act(async () => {
      fireEvent.click(getByRole('button', { name: 'Vote' }));
    });
    expect(store.actions).toContainEqual(
      expect.objectContaining({ type: VOTE_POLL, path: PATH }),
    );
    expect(kinds()).toEqual(['thanks']);
  });

  it('says why a vote failed', () => {
    const { kinds, form } = setup(
      {},
      entry(open, { voteError: { status: 500 } }),
    );
    expect(kinds()).toEqual(['voteFailed']);
    expect(form()).not.toBeNull();
  });

  it('turns the vote off when not interactive', () => {
    const { container } = setup({ interactive: false }, entry(open));
    expect(container.querySelector('fieldset')?.matches(':disabled')).toBe(
      true,
    );
  });

  it('shows the fallback options until the state arrives', () => {
    const { form, container } = setup({ fallbackOptions: open.options });
    expect(form()).not.toBeNull();
    expect(container.querySelector('fieldset')?.matches(':disabled')).toBe(
      true,
    );
    expect(container.querySelector('.poll')?.getAttribute('aria-busy')).toBe(
      'true',
    );
  });

  it('uses the default legend, not the question, for a single choice poll', () => {
    const { getByRole } = setup({ title: 'Do you like polls?' }, entry(open));
    expect(getByRole('group', { name: 'Select one option' })).toBeTruthy();
  });

  it('offers checkboxes under the legend of a multiple choice poll', () => {
    const notVoted = {
      ...multiple,
      has_voted: false,
      total_votes: null,
      results: null,
    };
    const { getByRole, getAllByRole } = setup({}, entry(notVoted));
    expect(getByRole('group', { name: multiple.legend })).toBeTruthy();
    expect(getAllByRole('checkbox')).toHaveLength(3);
  });

  it('votes for every option checked', () => {
    const notVoted = {
      ...multiple,
      shuffle_options: false,
      has_voted: false,
      total_votes: null,
      results: null,
    };
    const { getByRole, store } = setup({}, entry(notVoted));
    fireEvent.click(getByRole('checkbox', { name: 'Red' }));
    fireEvent.click(getByRole('checkbox', { name: 'Blue' }));
    fireEvent.click(getByRole('button', { name: 'Vote' }));
    expect(store.actions).toContainEqual(
      expect.objectContaining({
        type: VOTE_POLL,
        request: expect.objectContaining({ data: { option_ids: [0, 2] } }),
      }),
    );
  });

  describe('shuffled options', () => {
    const notVoted = {
      ...multiple,
      has_voted: false,
      total_votes: null,
      results: null,
    };
    const labels = (container: HTMLElement) =>
      Array.from(container.querySelectorAll('.poll-form__option label')).map(
        (label) => label.textContent,
      );

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it('shows the options in a random order', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0);
      const { container } = setup({}, entry(notVoted));
      expect(labels(container)).toEqual(['Green', 'Blue', 'Red']);
    });

    it('keeps the poll order when the poll does not shuffle', () => {
      const random = vi.spyOn(Math, 'random').mockReturnValue(0);
      const { container } = setup(
        {},
        entry({ ...notVoted, shuffle_options: false }),
      );
      expect(labels(container)).toEqual(['Red', 'Green', 'Blue']);
      expect(random).not.toHaveBeenCalled();
    });

    it('still votes for the options checked', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0);
      const { getByRole, store } = setup({}, entry(notVoted));
      fireEvent.click(getByRole('checkbox', { name: 'Red' }));
      fireEvent.click(getByRole('checkbox', { name: 'Blue' }));
      fireEvent.click(getByRole('button', { name: 'Vote' }));
      const voted = store.actions.find(
        (a: { type: string }) => a.type === VOTE_POLL,
      );
      expect([...voted.request.data.option_ids].sort()).toEqual([0, 2]);
    });

    it('keeps the results in the poll order', () => {
      vi.spyOn(Math, 'random').mockReturnValue(0);
      const { container } = setup({}, entry(multiple));
      const rows = Array.from(
        container.querySelectorAll('table.poll-results-numbers tbody th'),
      ).map((th) => th.textContent);
      expect(rows).toEqual(['Red', 'Green', 'Blue']);
    });
  });

  it('draws bars when a multiple choice poll asks for a pie', () => {
    const { container } = setup(
      {},
      entry({ ...multiple, results_graph: 'pie' }),
    );
    expect(container.querySelector('.poll-results-pie')).toBeNull();
    expect(container.querySelector('.poll-results-bar')).not.toBeNull();
  });

  it('keeps the pie of a single choice poll', () => {
    const { container } = setup(
      {},
      entry({ ...openVoted, results_graph: 'pie' }),
    );
    expect(container.querySelector('.poll-results-pie')).not.toBeNull();
  });

  it('shows a multiple choice poll as such until the state arrives', () => {
    const { getByRole, getAllByRole } = setup({
      fallbackOptions: multiple.options,
      fallbackMaxChoices: 2,
      fallbackLegend: null,
    });
    expect(getByRole('group', { name: 'Select up to 2 options' })).toBeTruthy();
    expect(getAllByRole('checkbox')).toHaveLength(3);
  });

  it('says so when the poll cannot be read', () => {
    const { kinds, form } = setup(
      { fallbackOptions: open.options },
      entry(null, { error: { status: 404 } }),
    );
    expect(kinds()).toEqual(['unavailable']);
    expect(form()).toBeNull();
  });

  it('shows the header, the linked question and the total', () => {
    const { getByRole, container } = setup(
      {
        header: 'Our poll',
        title: 'Do you like polls?',
        linkToPoll: true,
        showTotal: true,
      },
      entry(openVoted),
    );
    expect(getByRole('heading', { level: 2, name: 'Our poll' })).toBeTruthy();
    expect(
      getByRole('link', { name: 'Do you like polls?' }).getAttribute('href'),
    ).toBe(PATH);
    expect(container.querySelector('.poll-total-votes')?.textContent).toBe(
      'Total votes: 3',
    );
  });

  it('shows the question unlinked, and no total while voting', () => {
    const { queryByRole, container, getByText } = setup(
      { title: 'Do you like polls?', showTotal: true },
      entry(open),
    );
    expect(getByText('Do you like polls?', { selector: 'p' })).toBeTruthy();
    expect(queryByRole('link')).toBeNull();
    expect(container.querySelector('.poll-total-votes')).toBeNull();
  });
});

describe('statusKinds', () => {
  const poll = open as PollState;
  const error = (type?: string): PollError => ({ status: 403, type });

  it.each([
    ['nothing for a fresh vote', poll, false, false, null, []],
    ['thanks after voting', poll, true, true, null, ['thanks']],
    [
      'already voted on an AlreadyVoted error',
      poll,
      false,
      true,
      error('AlreadyVoted'),
      ['alreadyVoted'],
    ],
    [
      'a failed vote on any other error',
      poll,
      false,
      true,
      error('Unauthorized'),
      ['voteFailed'],
    ],
    [
      'not allowed without the permission',
      { ...poll, can_vote: false },
      false,
      false,
      null,
      ['notAllowed'],
    ],
    [
      'closed after having voted, without "already voted"',
      { ...poll, state: 'closed' },
      true,
      false,
      null,
      ['closed'],
    ],
    [
      'not open while pending',
      { ...poll, state: 'pending' },
      false,
      false,
      null,
      ['notOpen'],
    ],
  ] as [string, PollState, boolean, boolean, PollError | null, string[]][])(
    '%s',
    (_name, data, hasVoted, justVoted, voteError, expected) => {
      expect(statusKinds(data, hasVoted, justVoted, voteError)).toEqual(
        expected,
      );
    },
  );
});
