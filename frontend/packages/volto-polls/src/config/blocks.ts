import type { ConfigType } from '@plone/registry';
import PollBlockInfo, { POLL_BLOCK } from '../components/Blocks/Poll';

/**
 * Register the poll block, which shows a poll in any page.
 *
 * @param config - The Volto configuration registry.
 * @returns The same registry.
 */
export default function install(config: ConfigType) {
  config.blocks.blocksConfig[POLL_BLOCK] = PollBlockInfo;
  return config;
}
