import { defineConfig } from 'vitest/config';
import voltoVitestConfig from '@plone/volto/vitest.config.mjs';
import path from 'path';
import { fileURLToPath } from 'url';

const packageDir = path.dirname(fileURLToPath(import.meta.url));

const addonAlias = {
  '@plone-collective/volto-polls': path.resolve(packageDir, 'src'),
  '@plone/volto': path.resolve(packageDir, '../../core/packages/volto/src'),
};

// `test.projects` each carry their own `resolve`, and a project's aliases win
// over the top-level ones -- so the add-on alias has to be merged into every
// project, not just the root config.
const projects = (voltoVitestConfig.test?.projects ?? []).map((project) => ({
  ...project,
  resolve: {
    ...project.resolve,
    alias: {
      ...(project.resolve?.alias ?? {}),
      ...addonAlias,
    },
  },
}));

export default defineConfig({
  ...voltoVitestConfig,
  resolve: {
    alias: {
      ...(voltoVitestConfig.resolve?.alias ?? {}),
      ...addonAlias,
    },
  },
  test: {
    ...voltoVitestConfig.test,
    projects,
  },
});
