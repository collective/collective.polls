/**
 * The anonymous vote cookie.
 *
 * When an anonymous visitor votes, the backend sets `collective.poll.<UID>`.
 * It is readable by scripts on purpose: the backend's answer to anonymous
 * visitors is the same for all of them, so it can be cached, and only the
 * browser knows whether this visitor voted.
 * @module helpers/cookie
 */

import { COOKIE_PREFIX } from '../constants/poll';

/**
 * Tell whether this browser voted in a poll, from its cookie.
 *
 * @param uid The poll's UID.
 * @param cookies The cookie string; `document.cookie` by default.
 * @returns `false` on the server, where there is no cookie to read.
 */
export function hasVotedCookie(uid: string, cookies?: string): boolean {
  const source =
    cookies ?? (typeof document === 'undefined' ? '' : document.cookie);
  const name = `${COOKIE_PREFIX}${uid}`;
  return source.split(';').some((pair) => {
    const [key, ...rest] = pair.trim().split('=');
    return key === name && rest.join('=') !== '';
  });
}
