import type { ConfigType } from '@plone/registry';
import { latestPolls, polls } from '../reducers/polls';

/**
 * Register the add-on's reducers: `polls`, the state of each poll by path,
 * and `latestPolls`, the newest poll found by each search.
 *
 * @param config - The Volto configuration registry.
 * @returns The same registry.
 */
export default function install(config: ConfigType) {
  config.addonReducers = {
    ...config.addonReducers,
    polls,
    latestPolls,
  };
  return config;
}
