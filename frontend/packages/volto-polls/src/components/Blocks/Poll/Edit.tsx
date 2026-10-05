import React from 'react';
import SidebarPortal from '@plone/volto/components/manage/Sidebar/SidebarPortal';
import PollBlockDataForm from './Data';
import PollBlockView from './View';
import type { PollBlockData } from '../../../types/poll';

export interface PollBlockEditProps {
  data: PollBlockData;
  block: string;
  selected: boolean;
  onChangeBlock: (id: string, data: PollBlockData) => void;
}

/** The poll block in the editor: the poll, without voting, and its settings. */
export const PollBlockEdit = ({
  data,
  block,
  selected,
  onChangeBlock,
}: PollBlockEditProps) => (
  <>
    <PollBlockView data={data} isEditMode />
    <SidebarPortal selected={selected}>
      <PollBlockDataForm
        data={data}
        block={block}
        onChangeBlock={onChangeBlock}
      />
    </SidebarPortal>
  </>
);

export default PollBlockEdit;
