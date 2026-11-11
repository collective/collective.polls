import React from 'react';
import SidebarPortal from '@plone/volto/components/manage/Sidebar/SidebarPortal';
import PollBlockDataForm, { type PollBlockDataProps } from './Data';
import PollBlockView from './View';

export interface PollBlockEditProps extends PollBlockDataProps {
  selected: boolean;
}

/**
 * The poll block in the editor: the poll, without voting, and its settings.
 *
 * Every prop Volto gives the block reaches its sidebar form, as core does
 * with its own forms.
 */
export const PollBlockEdit = (props: PollBlockEditProps) => {
  const { data, selected } = props;
  return (
    <>
      <PollBlockView data={data} isEditMode />
      <SidebarPortal selected={selected}>
        <PollBlockDataForm {...props} />
      </SidebarPortal>
    </>
  );
};

export default PollBlockEdit;
