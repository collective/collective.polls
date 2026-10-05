import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import PollForm from './PollForm';
import open from '../../__fixtures__/open.json';

const withWrapper: Decorator = (Story) => (
  <Wrapper anonymous>
    <div style={{ padding: 24, maxWidth: 480 }}>
      <Story />
    </div>
  </Wrapper>
);

const meta = {
  title: 'Polls/PollForm',
  component: PollForm,
  decorators: [withWrapper],
  tags: ['autodocs'],
  args: { options: open.options, onVote: () => undefined },
} satisfies Meta<typeof PollForm>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
/** Choose an option: the vote button turns on. */
export const WithQuestion: Story = { args: { legend: 'Do you like polls?' } };
export const Submitting: Story = { args: { submitting: true } };
export const Disabled: Story = { args: { disabled: true } };
