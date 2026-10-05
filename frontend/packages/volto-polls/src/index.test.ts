import { describe, it, expect } from 'vitest';
import config from '@plone/volto/registry';
import applyConfig from './index';
import Poll from './components/Poll/Poll';
import PollView from './components/Views/PollView/PollView';
import PollBlockInfo from './components/Blocks/Poll';
import PollOptionsWidget from './components/Widgets/PollOptionsWidget/PollOptionsWidget';
import { polls } from './reducers/polls';

describe('applyConfig', () => {
  it('installs everything the add-on provides', () => {
    applyConfig(config as any);
    expect(config.views.contentTypesViews['collective.polls.poll']).toBe(
      PollView,
    );
    expect(config.blocks.blocksConfig.poll).toBe(PollBlockInfo);
    expect(config.widgets.widget.poll_options).toBe(PollOptionsWidget);
    expect(config.getComponent({ name: 'Poll' }).component).toBe(Poll);
    expect(
      config.getComponent({ name: 'PollResultsGraph', dependencies: ['pie'] })
        .component,
    ).toBeTruthy();
    expect(config.addonReducers?.polls).toBe(polls);
  });
});
