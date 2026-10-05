import React from 'react';
import { afterEach, describe, it, expect } from 'vitest';
import { Provider } from 'react-redux';
import config from '@plone/volto/registry';
import PollView from './PollView';
import { POLL_COMPONENT } from '../../../helpers/components';
import { recordingStore } from '../../../testing/store';
import { renderInVolto } from '../../../testing/render';
import { GET_POLL } from '../../../constants/ActionTypes';
import type { PollContent } from '../../../types/poll';
import open from '../../../__fixtures__/open.json';

const content = {
  '@id': 'http://localhost:3000/folder/a-poll',
  '@type': 'collective.polls.poll',
  title: 'Do you like polls?',
  description: 'A question for everyone.',
  options: open.options,
} as unknown as PollContent;

function setup(data: Partial<PollContent> = {}) {
  const store = recordingStore({ polls: {}, userSession: {} });
  const utils = renderInVolto(
    <Provider store={store as any}>
      <PollView content={{ ...content, ...data } as PollContent} />
    </Provider>,
  );
  return { store, ...utils };
}

describe('PollView', () => {
  afterEach(() => {
    delete (config as any)._data.components[POLL_COMPONENT];
  });

  it('shows the title and the description', () => {
    const { getByRole, getByText } = setup();
    expect(
      getByRole('heading', { level: 1, name: 'Do you like polls?' }),
    ).toBeTruthy();
    expect(getByText('A question for everyone.')).toBeTruthy();
  });

  it('leaves out an empty description', () => {
    const { container } = setup({ description: '' });
    expect(container.querySelector('.documentDescription')).toBeNull();
  });

  it('fetches the poll by its path and shows its options meanwhile', () => {
    const { store, getAllByRole } = setup();
    expect(store.actions).toContainEqual(
      expect.objectContaining({ type: GET_POLL, path: '/folder/a-poll' }),
    );
    expect(getAllByRole('radio')).toHaveLength(open.options.length);
  });

  it('sits in a plain container when none is registered', () => {
    const { container } = setup();
    expect(
      container.querySelector('div#page-document.ui.container'),
    ).not.toBeNull();
  });

  it('sits in the registered container', () => {
    const Box = ({ children, ...props }: any) => (
      <section data-box {...props}>
        {children}
      </section>
    );
    config.registerComponent({ name: 'Container', component: Box });
    const { container } = setup();
    expect(
      container.querySelector('section[data-box]#page-document'),
    ).not.toBeNull();
    delete (config as any)._data.components.Container;
  });

  it('displays the poll with the registered component', () => {
    const Custom = ({ path }: { path: string }) => (
      <div className="custom-poll">{path}</div>
    );
    config.registerComponent({
      name: POLL_COMPONENT,
      component: Custom as any,
    });
    const { container } = setup();
    expect(container.querySelector('.custom-poll')?.textContent).toBe(
      '/folder/a-poll',
    );
    expect(container.querySelector('.poll')).toBeNull();
  });
});
