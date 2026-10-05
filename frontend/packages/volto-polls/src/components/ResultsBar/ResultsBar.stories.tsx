import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import ResultsBar from './ResultsBar';
import { RESULT_SETS } from '../../testing/results';

const withWrapper: Decorator = (Story) => (
  <Wrapper anonymous>
    <div style={{ padding: 24, maxWidth: 480 }}>
      <Story />
    </div>
  </Wrapper>
);

const meta = {
  title: 'Polls/Results/ResultsBar',
  component: ResultsBar,
  decorators: [withWrapper],
  tags: ['autodocs'],
} satisfies Meta<typeof ResultsBar>;

export default meta;
type Story = StoryObj<typeof meta>;

export const SeveralOptions: Story = { args: { results: RESULT_SETS.several } };
export const AZeroOption: Story = {
  args: { results: RESULT_SETS.aZeroOption },
};
export const AllZero: Story = { args: { results: RESULT_SETS.allZero } };
export const OneAtFull: Story = { args: { results: RESULT_SETS.oneAtFull } };
