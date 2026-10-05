import type { BlockConfigBase } from '@plone/types';
import icon from '../../../icons/poll.svg';
import PollBlockEdit from './Edit';
import PollBlockView from './View';
import { PollBlockSchema } from './schema';

/** The id the block is registered and stored under. */
export const POLL_BLOCK = 'poll';

const PollBlockInfo: BlockConfigBase = {
  id: POLL_BLOCK,
  title: 'Poll',
  icon,
  group: 'common',
  view: PollBlockView as unknown as BlockConfigBase['view'],
  edit: PollBlockEdit as unknown as BlockConfigBase['edit'],
  blockSchema: PollBlockSchema as unknown as BlockConfigBase['blockSchema'],
  restricted: false,
  mostUsed: false,
  sidebarTab: 1,
};

export default PollBlockInfo;
