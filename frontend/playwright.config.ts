import { defineConfig, devices } from '@playwright/test';

// Acceptance tests run against a Plone acceptance backend (the
// VOLTO_ROBOT_TESTING layer, with RobotRemote enabled) and a running Volto
// frontend with this add-on. They live next to this config, in `acceptance/`.
export default defineConfig({
  testDir: 'acceptance/tests',
  testMatch: ['**/*.{spec,test}.{ts,tsx}'],
  outputDir: 'acceptance/results',
  // One worker: every test resets the shared backend before it runs.
  workers: 1,
  // Fail the build on CI if test.only was left in the source code.
  forbidOnly: !!process.env.CI,
  // Retry on CI only.
  retries: process.env.CI ? 3 : 0,
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        viewport: { width: 1440, height: 1000 },
      },
    },
  ],
});
