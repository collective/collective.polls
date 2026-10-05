import type { ConfigType } from '@plone/registry';
import type { BlockConfigBase } from '@plone/types';
import PollBlockInfo, { POLL_BLOCK } from '../components/Blocks/Poll';

/** A block holding other blocks, such as the grid. */
export type ContainerBlockConfig = BlockConfigBase & {
  allowedBlocks?: string[];
};

/**
 * Register the poll block, which shows a poll in any page or grid.
 *
 * Volto gives the grid its own copy of the blocks registered before any
 * add-on, so the block goes into that copy too, besides the allowed list.
 *
 * @param config - The Volto configuration registry.
 * @returns The same registry.
 */
export default function install(config: ConfigType) {
  const { blocksConfig } = config.blocks;
  blocksConfig[POLL_BLOCK] = PollBlockInfo;
  const grid = blocksConfig.gridBlock as ContainerBlockConfig | undefined;
  if (grid) {
    if (grid.allowedBlocks && !grid.allowedBlocks.includes(POLL_BLOCK)) {
      grid.allowedBlocks = [...grid.allowedBlocks, POLL_BLOCK];
    }
    if (grid.blocksConfig) grid.blocksConfig[POLL_BLOCK] = PollBlockInfo;
  }
  return config;
}
