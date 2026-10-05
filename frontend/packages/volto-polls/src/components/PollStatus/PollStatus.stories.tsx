import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import PollStatus from './PollStatus';

const withWrapper: Decorator = (Story) => (
  <Wrapper anonymous>
    <div style={{ padding: 24, maxWidth: 480 }}>
      <Story />
    </div>
  </Wrapper>
);

const meta = {
  title: 'Polls/PollStatus',
  component: PollStatus,
  decorators: [withWrapper],
  tags: ['autodocs'],
} satisfies Meta<typeof PollStatus>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Thanks: Story = { args: { kinds: ['thanks'] } };
export const Closed: Story = { args: { kinds: ['closed'] } };
export const NotOpen: Story = { args: { kinds: ['notOpen'] } };
export const AlreadyVoted: Story = { args: { kinds: ['alreadyVoted'] } };
export const NotAllowed: Story = { args: { kinds: ['notAllowed'] } };
export const AnonymousBlocked: Story = {
  args: { kinds: ['anonymousBlocked'] },
};
export const VoteFailed: Story = { args: { kinds: ['voteFailed'] } };
export const Unavailable: Story = { args: { kinds: ['unavailable'] } };
