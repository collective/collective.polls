import type { ConfigType } from '@plone/registry';
import type { ViewsConfig } from '@plone/types';
import PollView from '../components/Views/PollView/PollView';
import { POLL_TYPE } from '../constants/poll';

/**
 * Register the view of a poll.
 *
 * @param config - The Volto configuration registry.
 * @returns The same registry.
 */
export default function install(config: ConfigType) {
  // `config.views` may be typed as empty; Volto fills it before add-ons run.
  config.views = {
    ...config.views,
    contentTypesViews: {
      ...config.views?.contentTypesViews,
      [POLL_TYPE]: PollView,
    },
  } as unknown as ViewsConfig;
  return config;
}
