import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { renderInVolto } from '../../../testing/render';
import PollBlockDataForm from './Data';
import type { PollBlockData } from '../../../types/poll';

const seen: { schema?: any; onChangeField?: (id: string, v: unknown) => void } =
  {};

vi.mock('@plone/volto/components/manage/Form', () => ({
  BlockDataForm: ({
    schema,
    onChangeField,
  }: {
    schema: unknown;
    onChangeField: (id: string, v: unknown) => void;
  }) => {
    seen.schema = schema;
    seen.onChangeField = onChangeField;
    return null;
  },
}));

function renderForm(data: PollBlockData, onChangeBlock = vi.fn()) {
  renderInVolto(
    <PollBlockDataForm data={data} block="b" onChangeBlock={onChangeBlock} />,
  );
  return onChangeBlock;
}

describe('PollBlockDataForm', () => {
  it('builds the schema for the block data', () => {
    renderForm({ mode: 'chosen' });
    expect(seen.schema.title).toBe('Poll');
    expect(seen.schema.fieldsets[0].fields).toContain('poll');
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
