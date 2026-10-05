import { describe, it, expect, vi } from 'vitest';
import { fireEvent } from '@testing-library/react';
import PollForm from './PollForm';
import { renderInVolto } from '../../testing/render';
import open from '../../__fixtures__/open.json';

const options = open.options;

function setup(props: Partial<React.ComponentProps<typeof PollForm>> = {}) {
  const onVote = vi.fn();
  const utils = renderInVolto(
    <PollForm options={options} onVote={onVote} {...props} />,
  );
  return { onVote, ...utils };
}

describe('PollForm', () => {
  it('offers one radio per option, in a labelled group', () => {
    const { getByRole, getAllByRole } = setup();
    expect(getByRole('group', { name: 'Available options:' })).toBeTruthy();
    expect(getAllByRole('radio').map((r) => r.getAttribute('value'))).toEqual([
      '0',
      '1',
    ]);
    expect(getByRole('radio', { name: 'Yes' })).toBeTruthy();
  });

  it('uses the question as the legend', () => {
    const { getByRole } = setup({ legend: 'Do you like polls?' });
    expect(getByRole('group', { name: 'Do you like polls?' })).toBeTruthy();
  });

  it('keeps the vote button disabled until an option is chosen', () => {
    const { getByRole } = setup();
    const button = getByRole('button', { name: 'Vote' }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
    fireEvent.click(getByRole('radio', { name: 'No' }));
    expect(button.disabled).toBe(false);
  });

  it('votes for the chosen option, option 0 included', () => {
    const { getByRole, onVote } = setup();
    fireEvent.click(getByRole('radio', { name: 'Yes' }));
    fireEvent.click(getByRole('button', { name: 'Vote' }));
    expect(onVote).toHaveBeenCalledWith(0);
  });

  it('does not vote while a vote is in flight', () => {
    const { getByRole, onVote, container } = setup({ submitting: true });
    expect(
      (getByRole('button', { name: 'Vote' }) as HTMLButtonElement).disabled,
    ).toBe(true);
    expect(container.querySelector('form')?.getAttribute('aria-busy')).toBe(
      'true',
    );
    fireEvent.submit(container.querySelector('form') as HTMLFormElement);
    expect(onVote).not.toHaveBeenCalled();
  });

  it('shows the options without voting when disabled', () => {
    const { getAllByRole, getByRole, onVote, container } = setup({
      disabled: true,
    });
    expect(getAllByRole('radio').every((r) => r.matches(':disabled'))).toBe(
      true,
    );
    expect(
      (getByRole('button', { name: 'Vote' }) as HTMLButtonElement).disabled,
    ).toBe(true);
    fireEvent.submit(container.querySelector('form') as HTMLFormElement);
    expect(onVote).not.toHaveBeenCalled();
  });

  it('does not submit with nothing chosen', () => {
    const { onVote, container } = setup();
    fireEvent.submit(container.querySelector('form') as HTMLFormElement);
    expect(onVote).not.toHaveBeenCalled();
  });
});
