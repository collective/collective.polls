import type { ConfigType } from '@plone/registry';
import pollSVG from '../icons/poll.svg';

/** The portal type of a poll, as the backend registers it. */
export const POLL_TYPE = 'collective.polls.poll';

/**
 * Give polls their icon wherever Volto lists content, such as the add menu.
 *
 * @param config - The Volto configuration registry.
 * @returns The same registry.
 */
export default function install(config: ConfigType) {
  config.settings.contentIcons = {
    ...config.settings.contentIcons,
    [POLL_TYPE]: pollSVG,
  };
  return config;
}
