import React, { useId, useState } from 'react';
import { defineMessages, useIntl } from 'react-intl';
import type { PollOption } from '../../types/poll';
import './poll-form.scss';

const messages = defineMessages({
  selectOne: { id: 'Select one option', defaultMessage: 'Select one option' },
  selectUpTo: {
    id: 'Select up to {count} options',
    defaultMessage: 'Select up to {count} options',
  },
  vote: { id: 'Vote', defaultMessage: 'Vote' },
});

export interface PollFormProps {
  /** The options to choose from, in order. */
  options: PollOption[];
  /** Called with the chosen options' ids, in option order. */
  onVote: (optionIds: number[]) => void;
  /** How many options a voter can pick; more than 1 turns on checkboxes. */
  maxChoices?: number;
  /** A vote is in flight. */
  submitting?: boolean;
  /** Show the options without letting anyone vote, as in a preview. */
  disabled?: boolean;
  /** Show only the options, without a vote button, as for a poll not open yet. */
  readOnly?: boolean;
  /**
   * Shown above the options. Empty means "Select one option", or "Select up
   * to n options" for a multiple choice poll.
   */
  legend?: string | null;
}

/**
 * The options of a poll and, unless read-only, a vote button.
 *
 * A single choice poll gets radio buttons, a multiple choice one gets
 * checkboxes, and the unchecked ones turn off once `maxChoices` are
 * checked. The button stays disabled until an option is chosen and while a
 * vote is in flight, so a double click cannot send two votes.
 */
export const PollForm = ({
  options,
  onVote,
  maxChoices = 1,
  submitting = false,
  disabled = false,
  readOnly = false,
  legend,
}: PollFormProps) => {
  const intl = useIntl();
  const name = useId();
  const [selected, setSelected] = useState<number[]>([]);
  const multiple = maxChoices > 1;
  const full = selected.length >= maxChoices;
  const off = disabled || readOnly;

  const toggle = (optionId: number) => {
    if (!multiple) {
      setSelected([optionId]);
    } else if (selected.includes(optionId)) {
      setSelected(selected.filter((id) => id !== optionId));
    } else if (!full) {
      setSelected([...selected, optionId]);
    }
  };

  const onSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (selected.length === 0 || submitting || off) return;
    const order = options.map((option) => option.option_id);
    onVote([...selected].sort((a, b) => order.indexOf(a) - order.indexOf(b)));
  };

  const fallback = multiple
    ? intl.formatMessage(messages.selectUpTo, { count: maxChoices })
    : intl.formatMessage(messages.selectOne);

  return (
    <form className="poll-form" onSubmit={onSubmit} aria-busy={submitting}>
      <fieldset disabled={off || submitting}>
        <legend>{legend || fallback}</legend>
        {options.map((option) => {
          const id = `${name}-${option.option_id}`;
          const checked = selected.includes(option.option_id);
          return (
            <div key={option.option_id} className="poll-form__option">
              <input
                type={multiple ? 'checkbox' : 'radio'}
                id={id}
                name={name}
                value={option.option_id}
                checked={checked}
                disabled={multiple && full && !checked}
                onChange={() => toggle(option.option_id)}
              />
              <label htmlFor={id}>{option.description}</label>
            </div>
          );
        })}
      </fieldset>
      {!readOnly && (
        <button
          type="submit"
          className="poll-form__submit"
          disabled={disabled || submitting || selected.length === 0}
        >
          {intl.formatMessage(messages.vote)}
        </button>
      )}
    </form>
  );
};

export default PollForm;
