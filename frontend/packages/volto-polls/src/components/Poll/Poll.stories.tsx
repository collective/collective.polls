import React from 'react';
import type { Decorator, Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import Wrapper from '@plone/volto/storybook';
import Poll from './Poll';
import { recordingStore } from '../../testing/store';
import closed from '../../__fixtures__/closed.json';
import open from '../../__fixtures__/open.json';
import openAnonymousBlocked from '../../__fixtures__/open-anonymous-blocked.json';
import openVoted from '../../__fixtures__/open-voted.json';
import privatePoll from '../../__fixtures__/private.json';

const PATH = '/a-poll';

/** A store holding one poll's state; voting changes nothing. */
const withPoll =
  (data: unknown, changes: Record<string, unknown> = {}): Decorator =>
  (Story) => (
    <Wrapper anonymous>
      <Provider
        store={
          recordingStore({
            userSession: {},
            polls: {
              [PATH]: {
                loading: false,
                loaded: Boolean(data),
                error: null,
                data,
                voting: false,
                voteError: null,
                ...changes,
              },
            },
          }) as any
        }
      >
        <div style={{ padding: 24, maxWidth: 520 }}>
          <Story />
        </div>
      </Provider>
    </Wrapper>
  );

const meta = {
  title: 'Polls/Poll',
  component: Poll,
  tags: ['autodocs'],
  args: { path: PATH, title: 'Do you like polls?' },
} satisfies Meta<typeof Poll>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Open: Story = { decorators: [withPoll(open)] };
export const Voted: Story = {
  args: { showTotal: true },
  decorators: [withPoll(openVoted)],
};
export const Closed: Story = {
  args: { showTotal: true },
  decorators: [withPoll(closed)],
};
export const NotOpen: Story = { decorators: [withPoll(privatePoll)] };
export const AnonymousBlocked: Story = {
  decorators: [withPoll(openAnonymousBlocked)],
};
/** A reviewer can look at the partial results before voting. */
export const ReviewerBeforeVoting: Story = {
  decorators: [withPoll({ ...openVoted, has_voted: false })],
};
export const VoteFailed: Story = {
  decorators: [withPoll(open, { voteError: { status: 500 } })],
};
/** As in a page being edited. */
export const NotInteractive: Story = {
  args: { interactive: false },
  decorators: [withPoll(open)],
};
/** What the server renders, before the browser asks for the state. */
export const Loading: Story = {
  args: { fallbackOptions: open.options },
  decorators: [withPoll(null)],
};
export const Unavailable: Story = {
  decorators: [withPoll(null, { error: { status: 404 } })],
};
export const InABlock: Story = {
  args: { header: 'Our poll', linkToPoll: true, showTotal: true },
  decorators: [withPoll(openVoted)],
};
