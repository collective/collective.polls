/**
 * Components other add-ons and projects can replace.
 * @module helpers/components
 */

import type React from 'react';
import config from '@plone/volto/registry';
import Poll, { type PollProps } from '../components/Poll/Poll';

/** The name the component that displays a poll is registered under. */
export const POLL_COMPONENT = 'Poll';

/**
 * Find the component that displays a poll.
 *
 * The poll view and the poll block both display a poll through it, so
 * registering another `Poll` component changes both.
 */
export function locatePoll(): React.ComponentType<PollProps> {
  const registered = config.getComponent?.({ name: POLL_COMPONENT })
    ?.component as React.ComponentType<PollProps> | undefined;
  return registered ?? Poll;
}
