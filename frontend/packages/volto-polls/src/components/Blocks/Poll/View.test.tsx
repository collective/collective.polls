import React from 'react';
import { afterEach, describe, it, expect } from 'vitest';
import { Provider } from 'react-redux';
import config from '@plone/volto/registry';
import PollBlockView from './View';
import { POLL_COMPONENT } from '../../../helpers/components';
import { recordingStore } from '../../../testing/store';
import { renderInVolto } from '../../../testing/render';
import { GET_LATEST_POLL, GET_POLL } from '../../../constants/ActionTypes';
import type { PollBlockData } from '../../../types/poll';

const NAVROOT = { data: { navroot: { '@id': 'http://localhost:3000/en' } } };

function found(path: string | null, title: string | null = null) {
  return { loading: false, loaded: true, error: null, path, title };
}

/** Render with a stand-in `Poll` that shows the props it gets. */
function setup(
  data: PollBlockData,
  latestPolls: Record<string, unknown> = {},
  isEditMode = false,
) {
  config.registerComponent({
    name: POLL_COMPONENT,
    component: ((props: Record<string, unknown>) => (
      <pre className="poll-props">{JSON.stringify(props)}</pre>
    )) as any,
  });
  const store = recordingStore({
    navroot: NAVROOT,
    latestPolls,
    polls: {},
    userSession: {},
  });
  const utils = renderInVolto(
    <Provider store={store as any}>
      <PollBlockView data={data} isEditMode={isEditMode} />
    </Provider>,
  );
  const props = () => {
    const pre = utils.container.querySelector('.poll-props');
    return pre ? JSON.parse(pre.textContent as string) : null;
  };
  const types = () => store.actions.map((a: { type: string }) => a.type);
  return { store, props, types, ...utils };
}

describe('PollBlockView', () => {
  afterEach(() => {
    delete (config as any)._data.components[POLL_COMPONENT];
  });

  it('searches for the latest open poll below the navigation root', () => {
    const { store } = setup({});
    expect(store.actions).toEqual([
      expect.objectContaining({ type: GET_LATEST_POLL, key: '/en|open' }),
    ]);
  });

  it('shows the latest open poll with its title', () => {
    const { props } = setup(
      { header: 'Our poll' },
      { '/en|open': found('http://localhost:3000/en/a-poll', 'A poll') },
    );
    expect(props()).toEqual({
      path: '/en/a-poll',
      title: 'A poll',
      header: 'Our poll',
      showTotal: true,
      linkToPoll: true,
      interactive: true,
    });
  });

  it('falls back to the latest closed poll when asked to', () => {
    const { props } = setup(
      { show_closed: true },
      {
        '/en|open': found(null),
        '/en|closed': found('/en/old-poll', 'Old poll'),
      },
    );
    expect(props()).toMatchObject({ path: '/en/old-poll', title: 'Old poll' });
  });

  it('shows a chosen poll without searching', () => {
    const { props, types } = setup({
      mode: 'chosen',
      poll: [{ '@id': 'http://localhost:3000/en/chosen', title: 'Chosen' }],
      show_total: false,
      link_poll: false,
    });
    expect(types()).not.toContain(GET_LATEST_POLL);
    expect(props()).toMatchObject({
      path: '/en/chosen',
      title: 'Chosen',
      showTotal: false,
      linkToPoll: false,
    });
  });

  it('takes the title of a chosen poll from either spelling', () => {
    const { props } = setup({
      mode: 'chosen',
      poll: [{ '@id': '/en/chosen', Title: 'Chosen' }],
    });
    expect(props()).toMatchObject({ title: 'Chosen' });
  });

  it('renders nothing with no poll', () => {
    const { container } = setup({}, { '/en|open': found(null) });
    expect(container.querySelector('.poll-block')).toBeNull();
  });

  it('renders nothing for a chosen poll not chosen yet', () => {
    const { container } = setup({ mode: 'chosen', poll: [] });
    expect(container.querySelector('.poll-block')).toBeNull();
  });

  it('says so in the editor when there is no poll', () => {
    const { getByText } = setup({}, { '/en|open': found(null) }, true);
    expect(getByText('There is no poll to show.')).toBeTruthy();
  });

  it('says nothing in the editor while still searching', () => {
    const { container } = setup({}, {}, true);
    expect(container.textContent).toBe('');
  });

  it('turns voting off in the editor', () => {
    const { props } = setup({}, { '/en|open': found('/en/a-poll') }, true);
    expect(props()).toMatchObject({ path: '/en/a-poll', interactive: false });
    // No title was found: JSON drops the undefined key.
    expect(props()).not.toHaveProperty('title');
  });

  it('uses the add-on poll when nothing is registered', () => {
    const store = recordingStore({
      navroot: NAVROOT,
      latestPolls: { '/en|open': found('/en/a-poll', 'A poll') },
      polls: {},
      userSession: {},
    });
    const { container } = renderInVolto(
      <Provider store={store as any}>
        <PollBlockView data={{}} />
      </Provider>,
    );
    expect(container.querySelector('.poll-block .poll')).not.toBeNull();
    expect(store.actions).toContainEqual(
      expect.objectContaining({ type: GET_POLL, path: '/en/a-poll' }),
    );
  });
});
