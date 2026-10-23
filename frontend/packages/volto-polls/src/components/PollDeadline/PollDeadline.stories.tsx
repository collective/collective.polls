import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import PollDeadline from './PollDeadline';

const withWrapper: Decorator = (Story) => (
  <Wrapper anonymous>
    <div style={{ padding: 24 }}>
      <Story />
    </div>
  </Wrapper>
);

const meta = {
  title: 'Polls/PollDeadline',
  component: PollDeadline,
  decorators: [withWrapper],
  tags: ['autodocs'],
} satisfies Meta<typeof PollDeadline>;

export default meta;
type Story = StoryObj<typeof meta>;

export const ClosesOn: Story = {
  args: { closeDate: '2099-12-31T23:00:00+00:00' },
};
