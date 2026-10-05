import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import PollForm from './PollForm';
import open from '../../__fixtures__/open.json';
import multiple from '../../__fixtures__/open-multiple.json';

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
export const WithLegend: Story = { args: { legend: 'Pick wisely' } };
/** Up to two choices: the third checkbox turns off once two are checked. */
export const MultipleChoice: Story = {
  args: { options: multiple.options, maxChoices: 2 },
};
export const MultipleChoiceWithLegend: Story = {
  args: {
    options: multiple.options,
    maxChoices: 2,
    legend: multiple.legend,
  },
};
export const Submitting: Story = { args: { submitting: true } };
export const Disabled: Story = { args: { disabled: true } };
export const ReadOnly: Story = { args: { readOnly: true } };
