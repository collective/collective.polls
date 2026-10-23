import { describe, it, expect } from 'vitest';
import PollDeadline from './PollDeadline';
import { renderInVolto } from '../../testing/render';

const CLOSE_DATE = '2099-12-31T23:00:00+00:00';

describe('PollDeadline', () => {
  it('says when voting closes', () => {
    const { container } = renderInVolto(
      <PollDeadline closeDate={CLOSE_DATE} />,
    );
    const text = container.querySelector('.poll-deadline')?.textContent;
    expect(text).toMatch(/^Voting closes on .*(2099|2100).*\.$/);
  });

  it('marks up the date for machines', () => {
    const { container } = renderInVolto(
      <PollDeadline closeDate={CLOSE_DATE} />,
    );
    expect(container.querySelector('time')?.getAttribute('dateTime')).toBe(
      CLOSE_DATE,
    );
  });
});
