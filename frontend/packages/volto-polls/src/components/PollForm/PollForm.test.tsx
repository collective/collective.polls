import { describe, it, expect, vi } from 'vitest';
import { fireEvent } from '@testing-library/react';
import PollForm from './PollForm';
import { renderInVolto } from '../../testing/render';
import open from '../../__fixtures__/open.json';
import multiple from '../../__fixtures__/open-multiple.json';

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
    expect(getByRole('group', { name: 'Select one option' })).toBeTruthy();
    expect(getAllByRole('radio').map((r) => r.getAttribute('value'))).toEqual([
      '0',
      '1',
    ]);
    expect(getByRole('radio', { name: 'Yes' })).toBeTruthy();
  });

  it('uses the legend given', () => {
    const { getByRole } = setup({ legend: 'Pick wisely' });
    expect(getByRole('group', { name: 'Pick wisely' })).toBeTruthy();
  });

  it('falls back to "Select one option" for an empty legend', () => {
    const { getByRole } = setup({ legend: null });
    expect(getByRole('group', { name: 'Select one option' })).toBeTruthy();
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
    expect(onVote).toHaveBeenCalledWith([0]);
  });

  it('keeps one choice in a single choice poll', () => {
    const { getByRole, onVote } = setup();
    fireEvent.click(getByRole('radio', { name: 'Yes' }));
    fireEvent.click(getByRole('radio', { name: 'No' }));
    fireEvent.click(getByRole('button', { name: 'Vote' }));
    expect(onVote).toHaveBeenCalledWith([1]);
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

  it('shows only the options when read-only', () => {
    const { getAllByRole, queryByRole, onVote, container } = setup({
      readOnly: true,
    });
    expect(getAllByRole('radio').every((r) => r.matches(':disabled'))).toBe(
      true,
    );
    expect(queryByRole('button')).toBeNull();
    fireEvent.submit(container.querySelector('form') as HTMLFormElement);
    expect(onVote).not.toHaveBeenCalled();
  });

  it('does not submit with nothing chosen', () => {
    const { onVote, container } = setup();
    fireEvent.submit(container.querySelector('form') as HTMLFormElement);
    expect(onVote).not.toHaveBeenCalled();
  });
});

describe('PollForm, multiple choice', () => {
  const colours = multiple.options;

  function setupMultiple(
    props: Partial<React.ComponentProps<typeof PollForm>> = {},
  ) {
    return setup({ options: colours, maxChoices: 2, ...props });
  }

  it('offers checkboxes, under "Select up to n options"', () => {
    const { getByRole, getAllByRole, queryAllByRole } = setupMultiple({
      legend: undefined,
    });
    expect(getByRole('group', { name: 'Select up to 2 options' })).toBeTruthy();
    expect(getAllByRole('checkbox')).toHaveLength(3);
    expect(queryAllByRole('radio')).toHaveLength(0);
  });

  it('uses the legend given', () => {
    const { getByRole } = setupMultiple({ legend: 'Pick your colours' });
    expect(getByRole('group', { name: 'Pick your colours' })).toBeTruthy();
  });

  it('votes for every option checked, in option order', () => {
    const { getByRole, onVote } = setupMultiple();
    fireEvent.click(getByRole('checkbox', { name: 'Blue' }));
    fireEvent.click(getByRole('checkbox', { name: 'Red' }));
    fireEvent.click(getByRole('button', { name: 'Vote' }));
    expect(onVote).toHaveBeenCalledWith([0, 2]);
  });

  it('turns the other options off once the limit is reached', () => {
    const { getByRole } = setupMultiple();
    fireEvent.click(getByRole('checkbox', { name: 'Red' }));
    expect(
      (getByRole('checkbox', { name: 'Green' }) as HTMLInputElement).disabled,
    ).toBe(false);
    fireEvent.click(getByRole('checkbox', { name: 'Blue' }));
    const green = getByRole('checkbox', { name: 'Green' }) as HTMLInputElement;
    expect(green.disabled).toBe(true);
    fireEvent.click(green);
    expect(green.checked).toBe(false);
  });

  it('unchecks an option, freeing a choice', () => {
    const { getByRole, onVote } = setupMultiple();
    fireEvent.click(getByRole('checkbox', { name: 'Red' }));
    fireEvent.click(getByRole('checkbox', { name: 'Blue' }));
    fireEvent.click(getByRole('checkbox', { name: 'Red' }));
    const green = getByRole('checkbox', { name: 'Green' }) as HTMLInputElement;
    expect(green.disabled).toBe(false);
    fireEvent.click(green);
    fireEvent.click(getByRole('button', { name: 'Vote' }));
    expect(onVote).toHaveBeenCalledWith([1, 2]);
  });

  it('votes with a single option checked', () => {
    const { getByRole, onVote } = setupMultiple();
    const button = getByRole('button', { name: 'Vote' }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
    fireEvent.click(getByRole('checkbox', { name: 'Green' }));
    expect(button.disabled).toBe(false);
    fireEvent.click(button);
    expect(onVote).toHaveBeenCalledWith([1]);
  });
});
