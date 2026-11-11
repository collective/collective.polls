import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import PollBlockEdit from './Edit';

vi.mock('@plone/volto/components/manage/Sidebar/SidebarPortal', () => ({
  default: ({
    selected,
    children,
  }: {
    selected: boolean;
    children: React.ReactNode;
  }) => (selected ? <div data-testid="sidebar">{children}</div> : null),
}));

const formProps = vi.hoisted(() => ({ seen: {} as Record<string, unknown> }));

vi.mock('./Data', () => ({
  default: (props: { block: string; [key: string]: unknown }) => {
    formProps.seen = props;
    return <div data-testid="data-form" data-block={props.block} />;
  },
}));

vi.mock('./View', () => ({
  default: ({ isEditMode }: { isEditMode: boolean }) => (
    <div data-testid="view" data-edit={String(isEditMode)} />
  ),
}));

function renderEdit(selected: boolean) {
  return render(
    <PollBlockEdit
      data={{ '@type': 'poll' }}
      block="b1"
      selected={selected}
      onChangeBlock={vi.fn()}
    />,
  );
}

describe('PollBlockEdit', () => {
  it('shows the view in edit mode', () => {
    const { getByTestId } = renderEdit(false);
    expect(getByTestId('view').getAttribute('data-edit')).toBe('true');
  });

  it('opens the settings only while the block is selected', () => {
    expect(renderEdit(false).queryByTestId('sidebar')).toBeNull();
    const { getByTestId } = renderEdit(true);
    expect(getByTestId('data-form').getAttribute('data-block')).toBe('b1');
  });

  it('hands the sidebar form the props Volto gives the block', () => {
    const blocksErrors = { b1: {} };
    const blocksConfig = { poll: {} };
    render(
      <PollBlockEdit
        data={{ '@type': 'poll' }}
        block="b1"
        selected
        onChangeBlock={vi.fn()}
        blocksConfig={blocksConfig}
        blocksErrors={blocksErrors}
        contentType="Document"
        navRoot={{ '@id': '/site' }}
      />,
    );
    expect(formProps.seen.blocksConfig).toBe(blocksConfig);
    expect(formProps.seen.blocksErrors).toBe(blocksErrors);
    expect(formProps.seen.contentType).toBe('Document');
    expect(formProps.seen.navRoot).toEqual({ '@id': '/site' });
  });
});
