import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import Wrapper from '@plone/volto/storybook';
import PollView from './PollView';
import { recordingStore } from '../../../testing/store';
import type { PollContent } from '../../../types/poll';
import openVoted from '../../../__fixtures__/open-voted.json';

const withPoll: Decorator = (Story) => (
  <Wrapper anonymous>
    <Provider
      store={
        recordingStore({
          userSession: {},
          polls: {
            '/a-poll': {
              loading: false,
              loaded: true,
              error: null,
              data: openVoted,
              voting: false,
              voteError: null,
            },
          },
        }) as any
      }
    >
      <Story />
    </Provider>
  </Wrapper>
);

const meta = {
  title: 'Polls/PollView',
  component: PollView,
  decorators: [withPoll],
  tags: ['autodocs'],
} satisfies Meta<typeof PollView>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    content: {
      '@id': '/a-poll',
      '@type': 'collective.polls.poll',
      title: 'Do you like polls?',
      description: 'A question for everyone.',
      options: openVoted.options,
    } as unknown as PollContent,
  },
};
