import React, { useState } from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import PollBlockDataForm from './Data';
import type { PollBlockData } from '../../../types/poll';

const withWrapper: Decorator = (Story) => (
  <Wrapper>
    <div id="sidebar" style={{ padding: 24, maxWidth: 400 }}>
      <Story />
    </div>
  </Wrapper>
);

/** Keep the data in state, as the block editor does. */
const Stateful = (args: React.ComponentProps<typeof PollBlockDataForm>) => {
  const [data, setData] = useState<PollBlockData>(args.data);
  return (
    <PollBlockDataForm
      {...args}
      data={data}
      onChangeBlock={(_id, next) => setData(next)}
    />
  );
};

const meta = {
  title: 'Polls/Blocks/Poll/Settings',
  component: PollBlockDataForm,
  decorators: [withWrapper],
  render: (args) => <Stateful {...args} />,
  args: { block: 'b1', onChangeBlock: () => undefined },
} satisfies Meta<typeof PollBlockDataForm>;

export default meta;
type Story = StoryObj<typeof meta>;

export const LatestPoll: Story = { args: { data: { '@type': 'poll' } } };
export const ChosenPoll: Story = {
  args: { data: { '@type': 'poll', mode: 'chosen' } },
};
