import { expect, test as base } from '@playwright/test';

import { setup, teardown } from './reset-fixture';

type TestFixtures = {
  resetBackend: void;
};

/**
 * The `test` every acceptance spec imports from here, not from
 * `@playwright/test`: each test starts from the backend's baseline and
 * leaves it clean for the next one.
 */
export const test = base.extend<TestFixtures>({
  resetBackend: [
    async ({ page, request }, use) => {
      await teardown(request);
      await setup(request);

      try {
        await use();
      } finally {
        // Close the live page before resetting the backend, so the teardown
        // does not trigger refresh noise that hides the real failure.
        await page.close().catch(() => {});
        await teardown(request);
      }
    },
    { auto: true },
  ],
});

export { expect };
