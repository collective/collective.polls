import { describe, it, expect } from 'vitest';
import PollStatus, { type PollStatusKind } from './PollStatus';
import { renderInVolto } from '../../testing/render';

const KINDS: [PollStatusKind, string, string][] = [
  ['thanks', 'Thanks for your vote', 'info'],
  ['closed', 'This poll is closed.', 'info'],
  ['notOpen', 'This poll is not open yet.', 'info'],
  ['alreadyVoted', 'You already voted in this poll.', 'info'],
  ['notAllowed', 'You are not authorized to vote', 'info'],
  ['anonymousBlocked', "Anonymous user won't be able to vote", 'warning'],
  ['voteFailed', 'Your vote could not be registered.', 'error'],
  ['unavailable', 'Nothing to see here', 'info'],
];

describe('PollStatus', () => {
  it.each(KINDS)('shows %s', (kind, text, level) => {
    const { getByRole } = renderInVolto(<PollStatus kinds={[kind]} />);
    const message = getByRole('status').querySelector('p');
    expect(message?.textContent).toContain(text);
    expect(message?.classList.contains(`poll-status__message--${level}`)).toBe(
      true,
    );
  });

  it('is a polite live region, rendered even when empty', () => {
    const { getByRole } = renderInVolto(<PollStatus kinds={[]} />);
    const region = getByRole('status');
    expect(region.getAttribute('aria-live')).toBe('polite');
    expect(region.children).toHaveLength(0);
  });

  it('shows several messages in order', () => {
    const { getByRole } = renderInVolto(
      <PollStatus kinds={['thanks', 'closed']} />,
    );
    expect(
      Array.from(getByRole('status').children).map((p) =>
        p.getAttribute('data-kind'),
      ),
    ).toEqual(['thanks', 'closed']);
  });
});
