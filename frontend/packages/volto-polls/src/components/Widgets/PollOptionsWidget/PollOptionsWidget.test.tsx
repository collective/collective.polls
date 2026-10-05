import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { fireEvent } from '@testing-library/react';
import PollOptionsWidget, { type EditedOption } from './PollOptionsWidget';
import { renderInVolto } from '../../../testing/render';

const OPTIONS: EditedOption[] = [
  { option_id: 0, description: 'Yes' },
  { option_id: 3, description: 'No' },
  { option_id: 7, description: 'Maybe' },
];

/** `setup()` uses `OPTIONS`; `setup(undefined)` really passes no value. */
function setup(
  ...args: [EditedOption[] | null | undefined, Record<string, unknown>?] | []
) {
  const value = args.length ? args[0] : OPTIONS;
  const props = args[1] ?? {};
  const onChange = vi.fn();
  const utils = renderInVolto(
    <PollOptionsWidget
      id="options"
      title="Available options"
      fieldSet="default"
      value={value}
      onChange={onChange}
      {...props}
    />,
  );
  const last = () => onChange.mock.calls.at(-1);
  return { onChange, last, ...utils };
}

describe('PollOptionsWidget', () => {
  it('shows one input per option, labelled by its number', () => {
    const { getByRole, getAllByRole } = setup();
    expect(getAllByRole('textbox')).toHaveLength(3);
    expect(
      (getByRole('textbox', { name: 'Option 2' }) as HTMLInputElement).value,
    ).toBe('No');
  });

  it('names the list after the field', () => {
    const { container } = setup();
    expect(container.querySelector('ol')?.getAttribute('aria-labelledby')).toBe(
      'fieldset-default-field-label-options',
    );
  });

  it('keeps the option id when the text changes', () => {
    const { getByRole, last } = setup();
    fireEvent.change(getByRole('textbox', { name: 'Option 2' }), {
      target: { value: 'Nope' },
    });
    expect(last()).toEqual([
      'options',
      [OPTIONS[0], { option_id: 3, description: 'Nope' }, OPTIONS[2]],
    ]);
  });

  it('adds an option without an id', () => {
    const { getByRole, last } = setup();
    fireEvent.click(getByRole('button', { name: 'Add Option' }));
    expect(last()?.[1]).toEqual([...OPTIONS, { description: '' }]);
  });

  it('removes an option', () => {
    const { getByRole, last } = setup();
    fireEvent.click(getByRole('button', { name: 'Delete Option: Option 1' }));
    expect(last()?.[1]).toEqual([OPTIONS[1], OPTIONS[2]]);
  });

  it('moves options, ids and all', () => {
    const { getByRole, last } = setup();
    fireEvent.click(getByRole('button', { name: 'Move option up: Option 3' }));
    expect(last()?.[1]).toEqual([OPTIONS[0], OPTIONS[2], OPTIONS[1]]);
    fireEvent.click(
      getByRole('button', { name: 'Move option down: Option 1' }),
    );
    expect(last()?.[1]).toEqual([OPTIONS[1], OPTIONS[0], OPTIONS[2]]);
  });

  it('cannot move the first option up or the last one down', () => {
    const { getByRole } = setup();
    expect(
      (
        getByRole('button', {
          name: 'Move option up: Option 1',
        }) as HTMLButtonElement
      ).disabled,
    ).toBe(true);
    expect(
      (
        getByRole('button', {
          name: 'Move option down: Option 3',
        }) as HTMLButtonElement
      ).disabled,
    ).toBe(true);
  });

  it.each([[null], [undefined], [[]]])(
    'starts a new poll with two blank options (%j)',
    (value) => {
      const { getAllByRole, getByText } = setup(value as any);
      expect(
        getAllByRole('textbox').map((i) => (i as HTMLInputElement).value),
      ).toEqual(['', '']);
      expect(
        getByText('You need to provide at least two options for a poll.'),
      ).toBeTruthy();
    },
  );

  it('asks for two options until two are filled in', () => {
    const { queryByText } = setup([
      { option_id: 0, description: 'Yes' },
      { description: '  ' },
    ]);
    expect(
      queryByText('You need to provide at least two options for a poll.'),
    ).not.toBeNull();
  });

  it('does not ask once two options are filled in', () => {
    const { queryByText } = setup();
    expect(
      queryByText('You need to provide at least two options for a poll.'),
    ).toBeNull();
  });

  it('turns everything off when disabled', () => {
    const { getAllByRole } = setup(OPTIONS, { isDisabled: true });
    expect(
      [...getAllByRole('textbox'), ...getAllByRole('button')].every((el) =>
        el.matches(':disabled'),
      ),
    ).toBe(true);
  });
});
