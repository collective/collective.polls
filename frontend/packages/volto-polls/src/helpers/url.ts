/**
 * Paths of polls.
 * @module helpers/url
 */

import { flattenToAppURL } from '@plone/volto/helpers/Url/Url';

/**
 * Turn a poll's URL into the path its state is stored and fetched under.
 *
 * Accepts the content `@id`, an object browser `@id` or the `@id` of a
 * `@poll` answer, and gives the same path for all three.
 *
 * @param url A URL or path of the poll.
 * @returns The path relative to the site, without a trailing slash.
 */
export function pollPath(url: string): string {
  return flattenToAppURL(url)
    .replace(/\/@poll$/, '')
    .replace(/\/+$/, '');
}
