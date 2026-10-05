import { describe, it, expect } from 'vitest';
import { createIntl } from 'react-intl';
import { PollBlockSchema } from './schema';
import { POLL_TYPE } from '../../../constants/poll';

const intl = createIntl({ locale: 'en' });

describe('PollBlockSchema', () => {
  it('shows the latest open poll by default', () => {
    const schema = PollBlockSchema({ intl });
    expect(schema.title).toBe('Poll');
    expect(schema.properties.mode.default).toBe('latest');
    expect(schema.fieldsets[0].fields).toEqual([
      'mode',
      'show_closed',
      'header',
      'show_total',
      'link_poll',
    ]);
  });

  it('asks for the poll only when one is chosen', () => {
    const schema = PollBlockSchema({ intl, data: { mode: 'chosen' } });
    expect(schema.fieldsets[0].fields).toEqual([
      'mode',
      'poll',
      'header',
      'show_total',
      'link_poll',
    ]);
  });

  it('lets only polls be chosen, one at most', () => {
    const { poll } = PollBlockSchema({ intl }).properties;
    expect(poll.widget).toBe('object_browser');
    expect(poll.selectableTypes).toEqual([POLL_TYPE]);
    expect(poll.maximumSelectionSize).toBe(1);
  });

  it('keeps the 2.x portlet defaults', () => {
    const { properties } = PollBlockSchema({ intl });
    expect(properties.show_total.default).toBe(true);
    expect(properties.show_closed.default).toBe(false);
    expect(properties.link_poll.default).toBe(true);
  });
});
