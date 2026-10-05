import { describe, it, expect } from 'vitest';
import TotalVotes from './TotalVotes';
import { renderInVolto } from '../../testing/render';

describe('TotalVotes', () => {
  it.each([
    [0, 'Total votes: 0'],
    [1, 'Total votes: 1'],
    [1234, 'Total votes: 1,234'],
  ])('shows %i votes', (total, text) => {
    const { container } = renderInVolto(<TotalVotes total={total} />);
    expect(container.querySelector('.poll-total-votes')?.textContent).toBe(
      text,
    );
  });
});
