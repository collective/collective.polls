import React from 'react';
import { defineMessages, useIntl } from 'react-intl';
import { useSelector } from 'react-redux';
import { flattenToAppURL } from '@plone/volto/helpers/Url/Url';
import { locatePoll } from '../../../helpers/components';
import { pollPath } from '../../../helpers/url';
import useLatestPoll from '../../../hooks/useLatestPoll';
import type { PollBlockData } from '../../../types/poll';

const messages = defineMessages({
  noPoll: {
    id: 'There is no poll to show.',
    defaultMessage: 'There is no poll to show.',
  },
});

export interface PollBlockViewProps {
  data: PollBlockData;
  /** Rendered by the block's edit: no voting, and a note when empty. */
  isEditMode?: boolean;
}

/**
 * A poll in any page: the latest open poll of the site section, or a
 * chosen one.
 *
 * The poll is displayed by the component registered as `Poll`, the same
 * one the poll view uses. With no poll to show the block renders nothing,
 * except in the editor.
 */
export const PollBlockView = ({
  data,
  isEditMode = false,
}: PollBlockViewProps) => {
  const intl = useIntl();
  const chosen = data.mode === 'chosen';
  const root = useSelector((state: any) =>
    flattenToAppURL(state.navroot?.data?.navroot?.['@id'] ?? ''),
  ) as string;
  const latest = useLatestPoll(root, Boolean(data.show_closed), !chosen);
  const picked = data.poll?.[0];
  const path = chosen ? (picked ? pollPath(picked['@id']) : null) : latest.path;
  const title = chosen ? picked?.title ?? picked?.Title : latest.title;
  const PollComponent = locatePoll();

  if (!path) {
    return isEditMode && latest.loaded ? (
      <div className="block poll-block poll-block--empty">
        <p>{intl.formatMessage(messages.noPoll)}</p>
      </div>
    ) : null;
  }
  return (
    <div className="block poll-block">
      <PollComponent
        path={path}
        title={title ?? undefined}
        header={data.header}
        showTotal={data.show_total ?? true}
        linkToPoll={data.link_poll ?? true}
        interactive={!isEditMode}
      />
    </div>
  );
};

export default PollBlockView;
