import { describe, it, expect } from 'vitest';
import type { ConfigType } from '@plone/registry';
import installBlocks, { type ContainerBlockConfig } from './blocks';
import PollBlockInfo from '../components/Blocks/Poll';

function makeConfig() {
  return {
    blocks: { blocksConfig: { title: { id: 'title' } } },
  } as unknown as ConfigType;
}

describe('installBlocks', () => {
  it('registers the poll block', () => {
    const config = installBlocks(makeConfig());
    expect(config.blocks.blocksConfig.poll).toBe(PollBlockInfo);
  });

  it('keeps the blocks Volto already registered', () => {
    const config = installBlocks(makeConfig());
    expect(config.blocks.blocksConfig.title).toEqual({ id: 'title' });
  });

  it('allows the block inside a grid', () => {
    const config = {
      blocks: {
        blocksConfig: {
          gridBlock: {
            allowedBlocks: ['image', 'slate'],
            blocksConfig: { image: { id: 'image' } },
          },
        },
      },
    } as unknown as ConfigType;
    const grid = installBlocks(config).blocks.blocksConfig
      .gridBlock as ContainerBlockConfig;
    expect(grid.allowedBlocks).toEqual(['image', 'slate', 'poll']);
    expect(grid.blocksConfig?.poll).toBe(PollBlockInfo);
    expect(grid.blocksConfig?.image).toEqual({ id: 'image' });
  });

  it('allows the block in a grid only once', () => {
    const config = {
      blocks: {
        blocksConfig: { gridBlock: { allowedBlocks: ['poll'] } },
      },
    } as unknown as ConfigType;
    const grid = installBlocks(config).blocks.blocksConfig
      .gridBlock as ContainerBlockConfig;
    expect(grid.allowedBlocks).toEqual(['poll']);
  });

  it('offers the block in any page, under the common group', () => {
    expect(PollBlockInfo).toMatchObject({
      id: 'poll',
      title: 'Poll',
      group: 'common',
      restricted: false,
      mostUsed: false,
      sidebarTab: 1,
    });
    expect(PollBlockInfo.icon).toBeTruthy();
  });
});
