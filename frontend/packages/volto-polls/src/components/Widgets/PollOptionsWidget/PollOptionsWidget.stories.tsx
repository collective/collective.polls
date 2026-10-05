import React, { useState } from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import Wrapper from '@plone/volto/storybook';
import PollOptionsWidget, { type EditedOption } from './PollOptionsWidget';

const withWrapper: Decorator = (Story) => (
  <Wrapper anonymous>
    <div className="ui form" style={{ padding: 24, maxWidth: 720 }}>
      <Story />
    </div>
  </Wrapper>
);

/** Keep the value in state, as the edit form does. */
const Stateful = (args: React.ComponentProps<typeof PollOptionsWidget>) => {
  const [value, setValue] = useState<EditedOption[] | null | undefined>(
    args.value,
  );
  return (
    <PollOptionsWidget
      {...args}
      value={value}
      onChange={(_id, next) => setValue(next)}
    />
  );
};

const meta = {
  title: 'Polls/PollOptionsWidget',
  component: PollOptionsWidget,
  decorators: [withWrapper],
  render: (args) => <Stateful {...args} />,
  args: {
    id: 'options',
    title: 'Available options',
    fieldSet: 'default',
    onChange: () => undefined,
  },
} satisfies Meta<typeof PollOptionsWidget>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NewPoll: Story = { args: { value: null } };
export const WithOptions: Story = {
  args: {
    value: [
      { option_id: 0, description: 'Yes' },
      { option_id: 1, description: 'No' },
      { option_id: 2, description: 'Maybe' },
    ],
  },
};
export const Disabled: Story = {
  args: {
    isDisabled: true,
    value: [
      { option_id: 0, description: 'Yes' },
      { option_id: 1, description: 'No' },
    ],
  },
};
