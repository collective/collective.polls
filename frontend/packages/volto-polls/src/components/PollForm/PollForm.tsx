import React, { useId, useState } from 'react';
import { defineMessages, useIntl } from 'react-intl';
import type { PollOption } from '../../types/poll';
import './poll-form.scss';

const messages = defineMessages({
  options: { id: 'Available options:', defaultMessage: 'Available options:' },
  vote: { id: 'Vote', defaultMessage: 'Vote' },
});

export interface PollFormProps {
  /** The options to choose from, in order. */
  options: PollOption[];
  /** Called with the chosen option's id. */
  onVote: (optionId: number) => void;
  /** A vote is in flight. */
  submitting?: boolean;
  /** Show the options without letting anyone vote, as in a preview. */
  disabled?: boolean;
  /** The question, used as the legend; "Available options:" by default. */
  legend?: string;
}

/**
 * One radio button per option and a vote button.
 *
 * The button stays disabled until an option is chosen and while a vote is
 * in flight, so a double click cannot send two votes.
 */
export const PollForm = ({
  options,
  onVote,
  submitting = false,
  disabled = false,
  legend,
}: PollFormProps) => {
  const intl = useIntl();
  const name = useId();
  const [selected, setSelected] = useState<number | null>(null);
  const onSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (selected !== null && !submitting && !disabled) onVote(selected);
  };
  return (
    <form className="poll-form" onSubmit={onSubmit} aria-busy={submitting}>
      <fieldset disabled={disabled || submitting}>
        <legend>{legend || intl.formatMessage(messages.options)}</legend>
        {options.map((option) => {
          const id = `${name}-${option.option_id}`;
          return (
            <div key={option.option_id} className="poll-form__option">
              <input
                type="radio"
                id={id}
                name={name}
                value={option.option_id}
                checked={selected === option.option_id}
                onChange={() => setSelected(option.option_id)}
              />
              <label htmlFor={id}>{option.description}</label>
            </div>
          );
        })}
      </fieldset>
      <button
        type="submit"
        className="poll-form__submit"
        disabled={disabled || submitting || selected === null}
      >
        {intl.formatMessage(messages.vote)}
      </button>
    </form>
  );
};

export default PollForm;
