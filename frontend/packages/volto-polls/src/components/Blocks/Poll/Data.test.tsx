import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { renderInVolto } from '../../../testing/render';
import PollBlockDataForm, { type PollBlockDataProps } from './Data';
import type { PollBlockData } from '../../../types/poll';

const seen: {
  schema?: any;
  onChangeField?: (id: string, v: unknown) => void;
  onChangeBlock?: unknown;
  block?: string;
  navRoot?: unknown;
  contentType?: string;
  errors?: unknown;
} = {};

vi.mock('@plone/volto/components/manage/Form', () => ({
  BlockDataForm: ({
    schema,
    onChangeField,
    onChangeBlock,
    block,
    navRoot,
    contentType,
    errors,
  }: {
    schema: unknown;
    onChangeField: (id: string, v: unknown) => void;
    onChangeBlock: unknown;
    block: string;
    navRoot?: unknown;
    contentType?: string;
    errors?: unknown;
  }) => {
    seen.schema = schema;
    seen.onChangeField = onChangeField;
    seen.onChangeBlock = onChangeBlock;
    seen.block = block;
    seen.navRoot = navRoot;
    seen.contentType = contentType;
    seen.errors = errors;
    return null;
  },
}));

function renderForm(
  data: PollBlockData,
  onChangeBlock = vi.fn(),
  extra: Partial<PollBlockDataProps> = {},
) {
  renderInVolto(
    <PollBlockDataForm
      data={data}
      block="b"
      onChangeBlock={onChangeBlock}
      {...extra}
    />,
  );
  return onChangeBlock;
}

describe('PollBlockDataForm', () => {
  it('builds the schema for the block data', () => {
    renderForm({ mode: 'chosen' });
    expect(seen.schema.title).toBe('Poll');
    expect(seen.schema.fieldsets[0].fields).toContain('poll');
  });

  it('reads the schema from the block configuration', () => {
    const blocksConfig = {
      poll: {
        blockSchema: () => ({
          title: 'Configured poll',
          fieldsets: [{ id: 'default', title: 'Settings', fields: [] }],
          properties: {},
        }),
      },
    };
    renderForm({ '@type': 'poll' }, vi.fn(), { blocksConfig });
    expect(seen.schema.title).toBe('Configured poll');
  });

  it('passes the page context and errors to the form, as core does', () => {
    const blocksErrors = { b: { poll: 'Required' } };
    renderForm({ '@type': 'poll' }, vi.fn(), {
      navRoot: { '@id': '/site' },
      contentType: 'Document',
      blocksErrors,
    });
    expect(seen.navRoot).toEqual({ '@id': '/site' });
    expect(seen.contentType).toBe('Document');
    expect(seen.errors).toBe(blocksErrors);
  });

  it('passes onChangeBlock down, which Volto needs to store the defaults', () => {
    const onChangeBlock = renderForm({ '@type': 'poll' });
    expect(seen.onChangeBlock).toBe(onChangeBlock);
    expect(seen.block).toBe('b');
  });

  it('patches the changed field onto the data', () => {
    const onChangeBlock = renderForm({ '@type': 'poll', header: 'H' });
    seen.onChangeField?.('show_total', false);
    expect(onChangeBlock).toHaveBeenCalledWith('b', {
      '@type': 'poll',
      header: 'H',
      show_total: false,
    });
  });
});
