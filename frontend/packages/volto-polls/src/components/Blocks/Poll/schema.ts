import { defineMessages, type IntlShape } from 'react-intl';
import type { JSONSchema } from '@plone/types';
import { POLL_TYPE } from '../../../constants/poll';
import type { PollBlockData } from '../../../types/poll';

const messages = defineMessages({
  poll: { id: 'Poll', defaultMessage: 'Poll' },
  settings: { id: 'Settings', defaultMessage: 'Settings' },
  mode: { id: 'Which poll', defaultMessage: 'Which poll' },
  modeDescription: {
    id: 'Which poll to show in the block.',
    defaultMessage: 'Which poll to show in the block.',
  },
  latest: { id: 'Latest opened poll', defaultMessage: 'Latest opened poll' },
  chosen: { id: 'A chosen poll', defaultMessage: 'A chosen poll' },
  chosenPoll: { id: 'Chosen poll', defaultMessage: 'Chosen poll' },
  header: { id: 'Header', defaultMessage: 'Header' },
  headerDescription: {
    id: 'The header for the block. Leave empty for none.',
    defaultMessage: 'The header for the block. Leave empty for none.',
  },
  showTotal: { id: 'Show total votes', defaultMessage: 'Show total votes' },
  showTotalDescription: {
    id: 'Show the number of collected votes so far.',
    defaultMessage: 'Show the number of collected votes so far.',
  },
  showClosed: { id: 'Show closed polls', defaultMessage: 'Show closed polls' },
  showClosedDescription: {
    id: 'When no poll is open, show the results of the latest closed one instead.',
    defaultMessage:
      'When no poll is open, show the results of the latest closed one instead.',
  },
  linkPoll: {
    id: 'Add a link to the poll',
    defaultMessage: 'Add a link to the poll',
  },
});

export interface PollBlockSchemaProps {
  intl: IntlShape;
  data?: PollBlockData;
}

/**
 * The settings of a poll block: the fields of the 2.x voting portlet.
 *
 * The poll picker appears only for a chosen poll, and the closed-poll
 * fallback only for the latest one.
 */
export const PollBlockSchema = ({
  intl,
  data = {},
}: PollBlockSchemaProps): JSONSchema => {
  const chosen = data.mode === 'chosen';
  return {
    title: intl.formatMessage(messages.poll),
    fieldsets: [
      {
        id: 'default',
        title: intl.formatMessage(messages.settings),
        fields: [
          'mode',
          ...(chosen ? ['poll'] : ['show_closed']),
          'header',
          'show_total',
          'link_poll',
        ],
      },
    ],
    properties: {
      mode: {
        title: intl.formatMessage(messages.mode),
        description: intl.formatMessage(messages.modeDescription),
        choices: [
          ['latest', intl.formatMessage(messages.latest)],
          ['chosen', intl.formatMessage(messages.chosen)],
        ],
        default: 'latest',
        noValueOption: false,
      },
      poll: {
        title: intl.formatMessage(messages.chosenPoll),
        widget: 'object_browser',
        mode: 'link',
        allowExternals: false,
        selectableTypes: [POLL_TYPE],
        maximumSelectionSize: 1,
        maximum: 1,
      },
      header: {
        title: intl.formatMessage(messages.header),
        description: intl.formatMessage(messages.headerDescription),
      },
      show_total: {
        title: intl.formatMessage(messages.showTotal),
        description: intl.formatMessage(messages.showTotalDescription),
        type: 'boolean',
        default: true,
      },
      show_closed: {
        title: intl.formatMessage(messages.showClosed),
        description: intl.formatMessage(messages.showClosedDescription),
        type: 'boolean',
        default: false,
      },
      link_poll: {
        title: intl.formatMessage(messages.linkPoll),
        type: 'boolean',
        default: true,
      },
    },
    required: [],
  } as JSONSchema;
};

export default PollBlockSchema;
