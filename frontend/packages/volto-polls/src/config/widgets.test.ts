import { describe, it, expect } from 'vitest';
import type { ConfigType } from '@plone/registry';
import installWidgets, { OPTIONS_WIDGET } from './widgets';
import PollOptionsWidget from '../components/Widgets/PollOptionsWidget/PollOptionsWidget';

function makeConfig() {
  return {
    widgets: { widget: { text: 'TextWidget' } },
  } as unknown as ConfigType;
}

describe('installWidgets', () => {
  it('registers the widget the backend asks for by name', () => {
    const config = installWidgets(makeConfig());
    expect(OPTIONS_WIDGET).toBe('poll_options');
    expect(config.widgets.widget.poll_options).toBe(PollOptionsWidget);
  });

  it('keeps the widgets Volto already registered', () => {
    const config = installWidgets(makeConfig());
    expect(config.widgets.widget.text).toBe('TextWidget');
  });
});
