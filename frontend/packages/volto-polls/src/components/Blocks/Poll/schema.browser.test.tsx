import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { fireEvent } from '@testing-library/react';
import ObjectBrowserBody from '@plone/volto/components/manage/Sidebar/ObjectBrowserBody';
import { renderInVolto } from '../../../testing/render';
import { PollBlockSchema } from './schema';
import { POLL_TYPE } from '../../../constants/poll';

const intl = {
  formatMessage: (m: { defaultMessage: string }) => m.defaultMessage,
};

const POLL = {
  '@id': 'http://localhost:3000/polls/a-poll',
  '@type': POLL_TYPE,
  title: 'A poll',
  is_folderish: true,
};

/**
 * Open Volto's object browser with the poll field's settings, as the
 * object browser widget does before anything was picked: `data` is the
 * browser's own default, an empty object.
 */
function renderBrowser() {
  const field = (
    PollBlockSchema({ intl: intl as any, data: { mode: 'chosen' } })
      .properties as any
  ).poll;
  const onSelectItem = vi.fn();
  const utils = renderInVolto(
    <ObjectBrowserBody
      block="b"
      data={{}}
      mode={field.mode}
      selectableTypes={field.selectableTypes}
      maximumSelectionSize={field.maximumSelectionSize}
      onSelectItem={onSelectItem}
      closeObjectBrowser={() => undefined}
      onChangeBlock={() => undefined}
      contextURL="/"
    />,
    {
      search: {
        subrequests: { 'b-link': { items: [POLL], loaded: true } },
      },
    },
  );
  return { onSelectItem, ...utils };
}

describe('the chosen poll field in the object browser', () => {
  it('selects a poll on click, before anything was picked', () => {
    const { onSelectItem, getByLabelText } = renderBrowser();
    fireEvent.click(getByLabelText('Select A poll'));
    expect(onSelectItem).toHaveBeenCalledWith(POLL['@id'], POLL);
  });
});
