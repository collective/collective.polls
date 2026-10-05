import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import PollResults from './PollResults';
import { RESULT_SETS } from '../../testing/results';

const withWrapper: Decorator = (Story) => (
  <Wrapper anonymous>
    <div style={{ padding: 24, maxWidth: 520 }}>
      <Story />
    </div>
  </Wrapper>
);

const meta = {
  title: 'Polls/Results/PollResults',
  component: PollResults,
  decorators: [withWrapper],
  tags: ['autodocs'],
  argTypes: {
    graph: { control: 'radio', options: ['bar', 'pie', 'numbers'] },
  },
} satisfies Meta<typeof PollResults>;

export default meta;
type Story = StoryObj<typeof meta>;

const results = RESULT_SETS.several;

export const BarOpen: Story = { args: { results, graph: 'bar' } };
export const BarClosed: Story = {
  args: { results, graph: 'bar', closed: true },
};
export const PieOpen: Story = { args: { results, graph: 'pie' } };
export const PieClosed: Story = {
  args: { results, graph: 'pie', closed: true },
};
export const NumbersOpen: Story = { args: { results, graph: 'numbers' } };
export const NumbersClosed: Story = {
  args: { results, graph: 'numbers', closed: true },
};
