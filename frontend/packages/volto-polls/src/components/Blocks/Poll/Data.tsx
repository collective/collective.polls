import React from 'react';
import { BlockDataForm } from '@plone/volto/components/manage/Form';
import { useIntl } from 'react-intl';
import { PollBlockSchema } from './schema';
import type { PollBlockData } from '../../../types/poll';

export interface PollBlockDataProps {
  data: PollBlockData;
  block: string;
  onChangeBlock: (id: string, data: PollBlockData) => void;
  /** The block registry, as Volto passes it to the block's edit. */
  blocksConfig?: Record<string, { blockSchema?: unknown } | undefined>;
  /** Validation errors of the blocks of the page. */
  blocksErrors?: Record<string, unknown>;
  contentType?: string;
  navRoot?: unknown;
}

/**
 * The sidebar form of a poll block.
 *
 * The schema comes from the block configuration, so the sidebar and the
 * `@blocks-schema` endpoint describe the block the same way. The props are
 * the ones core passes to its own block forms.
 */
export const PollBlockDataForm = ({
  data,
  block,
  onChangeBlock,
  blocksConfig,
  blocksErrors,
  contentType,
  navRoot,
}: PollBlockDataProps) => {
  const intl = useIntl();
  const id = data['@type'];
  const configured = id ? blocksConfig?.[id]?.blockSchema : undefined;
  const blockSchema = (configured ?? PollBlockSchema) as typeof PollBlockSchema;
  const schema = blockSchema({ intl, data });
  return (
    <BlockDataForm
      schema={schema}
      title={schema.title}
      onChangeField={(id: string, value: unknown) =>
        onChangeBlock(block, { ...data, [id]: value })
      }
      onChangeBlock={onChangeBlock}
      formData={data}
      block={block}
      navRoot={navRoot}
      contentType={contentType}
      errors={blocksErrors}
    />
  );
};

export default PollBlockDataForm;
