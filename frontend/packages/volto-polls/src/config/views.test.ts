import { describe, it, expect } from 'vitest';
import type { ConfigType } from '@plone/registry';
import installViews from './views';
import PollView from '../components/Views/PollView/PollView';

describe('installViews', () => {
  it('registers the poll view', () => {
    const config = installViews({ views: {} } as unknown as ConfigType);
    expect(config.views.contentTypesViews['collective.polls.poll']).toBe(
      PollView,
    );
  });

  it('keeps the views Volto already registered', () => {
    const config = installViews({
      views: {
        contentTypesViews: { Document: 'DocumentView' },
        layoutViews: { document_view: 'DocumentView' },
      },
    } as unknown as ConfigType);
    expect(config.views.contentTypesViews.Document).toBe('DocumentView');
    expect(config.views.layoutViews.document_view).toBe('DocumentView');
  });

  it('survives a registry with no views at all', () => {
    const config = installViews({} as unknown as ConfigType);
    expect(config.views.contentTypesViews['collective.polls.poll']).toBe(
      PollView,
    );
  });
});
