import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import Wrapper from '@plone/volto/storybook';
import PollBlockView from './View';
import { recordingStore } from '../../../testing/store';
import closed from '../../../__fixtures__/closed.json';
import open from '../../../__fixtures__/open.json';

function entry(data: unknown) {
  return {
    loading: false,
    loaded: true,
    error: null,
    data,
    voting: false,
    voteError: null,
  };
}

/** A site whose latest open poll is `/a-poll`, with `/old-poll` closed. */
const withSite =
  (openPoll: string | null): Decorator =>
  (Story) => (
    <Wrapper anonymous>
      <Provider
        store={
          recordingStore({
            userSession: {},
            navroot: { data: { navroot: { '@id': '' } } },
            latestPolls: {
              '|open': {
                loading: false,
                loaded: true,
                error: null,
                path: openPoll,
                title: openPoll ? 'Do you like polls?' : null,
              },
              '|closed': {
                loading: false,
                loaded: true,
                error: null,
                path: '/old-poll',
                title: 'An old poll',
              },
            },
            polls: { '/a-poll': entry(open), '/old-poll': entry(closed) },
          }) as any
        }
      >
        <div style={{ padding: 24, maxWidth: 520 }}>
          <Story />
        </div>
      </Provider>
    </Wrapper>
  );

const meta = {
  title: 'Polls/Blocks/Poll',
  component: PollBlockView,
  tags: ['autodocs'],
} satisfies Meta<typeof PollBlockView>;

export default meta;
type Story = StoryObj<typeof meta>;

export const LatestOpen: Story = {
  args: { data: { header: 'Our poll' } },
  decorators: [withSite('/a-poll')],
};
export const LatestClosed: Story = {
  args: { data: { show_closed: true } },
  decorators: [withSite(null)],
};
export const Chosen: Story = {
  args: {
    data: {
      mode: 'chosen',
      poll: [{ '@id': '/old-poll', title: 'An old poll' }],
      link_poll: false,
    },
  },
  decorators: [withSite('/a-poll')],
};
export const EmptyInTheEditor: Story = {
  args: { data: {}, isEditMode: true },
  decorators: [withSite(null)],
};
