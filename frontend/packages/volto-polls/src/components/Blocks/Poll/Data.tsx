import React from 'react';
import { BlockDataForm } from '@plone/volto/components/manage/Form';
import { useIntl } from 'react-intl';
import { PollBlockSchema } from './schema';
import type { PollBlockData } from '../../../types/poll';

export interface PollBlockDataProps {
  data: PollBlockData;
  block: string;
  onChangeBlock: (id: string, data: PollBlockData) => void;
}

/** The sidebar form of a poll block. */
export const PollBlockDataForm = ({
  data,
  block,
  onChangeBlock,
}: PollBlockDataProps) => {
  const intl = useIntl();
  const schema = PollBlockSchema({ intl, data });
  return (
    <BlockDataForm
      schema={schema}
      title={schema.title}
      onChangeField={(id: string, value: unknown) =>
        onChangeBlock(block, { ...data, [id]: value })
      }
      formData={data}
      block={block}
    />
  );
};

export default PollBlockDataForm;
