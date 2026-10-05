import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import Wrapper from '@plone/volto/storybook';
import PollBlockEdit from './Edit';
import { recordingStore } from '../../../testing/store';
import open from '../../../__fixtures__/open.json';

const withPoll: Decorator = (Story) => (
  <Wrapper>
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
              path: '/a-poll',
              title: 'Do you like polls?',
            },
          },
          polls: {
            '/a-poll': {
              loading: false,
              loaded: true,
              error: null,
              data: open,
              voting: false,
              voteError: null,
            },
          },
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
  title: 'Polls/Blocks/Poll/Edit',
  component: PollBlockEdit,
  decorators: [withPoll],
  args: {
    block: 'b1',
    selected: false,
    onChangeBlock: () => undefined,
  },
} satisfies Meta<typeof PollBlockEdit>;

export default meta;
type Story = StoryObj<typeof meta>;

/** The poll as it will look, with voting turned off. */
export const Default: Story = { args: { data: { '@type': 'poll' } } };
