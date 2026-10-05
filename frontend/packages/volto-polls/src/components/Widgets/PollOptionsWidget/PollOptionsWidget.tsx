import React from 'react';
import { defineMessages, useIntl } from 'react-intl';
import FormFieldWrapper from '@plone/volto/components/manage/Widgets/FormFieldWrapper';
import Icon from '@plone/volto/components/theme/Icon/Icon';
import addSVG from '@plone/volto/icons/add.svg';
import deleteSVG from '@plone/volto/icons/delete.svg';
import downSVG from '@plone/volto/icons/down-key.svg';
import upSVG from '@plone/volto/icons/up-key.svg';
import type { PollOption } from '../../../types/poll';
import './poll-options-widget.scss';

const messages = defineMessages({
  add: { id: 'Add Option', defaultMessage: 'Add Option' },
  remove: { id: 'Delete Option', defaultMessage: 'Delete Option' },
  up: { id: 'Move option up', defaultMessage: 'Move option up' },
  down: { id: 'Move option down', defaultMessage: 'Move option down' },
  option: { id: 'Option {number}', defaultMessage: 'Option {number}' },
  tooFew: {
    id: 'You need to provide at least two options for a poll.',
    defaultMessage: 'You need to provide at least two options for a poll.',
  },
});

/** An option being edited: new ones have no id until the backend gives one. */
export type EditedOption = Omit<PollOption, 'option_id'> & {
  option_id?: number;
};

export interface PollOptionsWidgetProps {
  id: string;
  title: string;
  description?: string;
  required?: boolean;
  error?: string[];
  fieldSet?: string;
  isDisabled?: boolean;
  value?: EditedOption[] | null;
  onChange: (id: string, value: EditedOption[]) => void;
}

/** What an empty poll starts with: two blank options. */
const BLANK: EditedOption[] = [{ description: '' }, { description: '' }];

/**
 * Edit the options of a poll: a text input per option, and buttons to add,
 * remove and reorder them.
 *
 * An option keeps its `option_id` through every edit, since votes are
 * counted by it; new options are sent without one, and the backend gives
 * them the next free id.
 */
export const PollOptionsWidget = (props: PollOptionsWidgetProps) => {
  const { id, value, onChange, isDisabled = false, fieldSet } = props;
  const intl = useIntl();
  const options = value && value.length > 0 ? value : BLANK;
  const filled = options.filter((o) => o.description.trim()).length;
  const labelId = `fieldset-${fieldSet}-field-label-${id}`;

  const change = (next: EditedOption[]) => onChange(id, next);
  const edit = (index: number, description: string) =>
    change(options.map((o, i) => (i === index ? { ...o, description } : o)));
  const remove = (index: number) =>
    change(options.filter((_o, i) => i !== index));
  const move = (index: number, offset: number) => {
    const next = [...options];
    [next[index], next[index + offset]] = [next[index + offset], next[index]];
    change(next);
  };

  return (
    <FormFieldWrapper
      {...props}
      noForInFieldLabel
      className="poll-options-widget"
    >
      <ol
        className="poll-options-widget__list"
        aria-labelledby={labelId}
        id={`field-${id}`}
      >
        {options.map((option, index) => {
          const number = index + 1;
          const label = intl.formatMessage(messages.option, { number });
          return (
            <li
              key={option.option_id ?? `new-${index}`}
              className="poll-options-widget__item"
            >
              <input
                type="text"
                id={`field-${id}-${index}`}
                aria-label={label}
                value={option.description}
                disabled={isDisabled}
                onChange={(event) => edit(index, event.target.value)}
              />
              <button
                type="button"
                className="poll-options-widget__button"
                aria-label={`${intl.formatMessage(messages.up)}: ${label}`}
                title={intl.formatMessage(messages.up)}
                disabled={isDisabled || index === 0}
                onClick={() => move(index, -1)}
              >
                <Icon name={upSVG} size="18px" />
              </button>
              <button
                type="button"
                className="poll-options-widget__button"
                aria-label={`${intl.formatMessage(messages.down)}: ${label}`}
                title={intl.formatMessage(messages.down)}
                disabled={isDisabled || index === options.length - 1}
                onClick={() => move(index, 1)}
              >
                <Icon name={downSVG} size="18px" />
              </button>
              <button
                type="button"
                className="poll-options-widget__button"
                aria-label={`${intl.formatMessage(messages.remove)}: ${label}`}
                title={intl.formatMessage(messages.remove)}
                disabled={isDisabled}
                onClick={() => remove(index)}
              >
                <Icon name={deleteSVG} size="18px" />
              </button>
            </li>
          );
        })}
      </ol>
      <button
        type="button"
        className="poll-options-widget__add"
        disabled={isDisabled}
        onClick={() => change([...options, { description: '' }])}
      >
        <Icon name={addSVG} size="18px" />
        {intl.formatMessage(messages.add)}
      </button>
      {filled < 2 && (
        <p className="poll-options-widget__hint">
          {intl.formatMessage(messages.tooFew)}
        </p>
      )}
    </FormFieldWrapper>
  );
};

export default PollOptionsWidget;
