import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import TotalVotes from './TotalVotes';

const withWrapper: Decorator = (Story) => (
  <Wrapper anonymous>
    <div style={{ padding: 24 }}>
      <Story />
    </div>
  </Wrapper>
);

const meta = {
  title: 'Polls/Results/TotalVotes',
  component: TotalVotes,
  decorators: [withWrapper],
  tags: ['autodocs'],
} satisfies Meta<typeof TotalVotes>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NoVotes: Story = { args: { total: 0 } };
export const OneVote: Story = { args: { total: 1 } };
export const ManyVotes: Story = { args: { total: 1234 } };
