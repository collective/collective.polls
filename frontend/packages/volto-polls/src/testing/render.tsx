/**
 * Render a component the way Volto's stories do: inside the storybook
 * `Wrapper`, which provides a mocked store, `react-intl` and a router.
 */
import React from 'react';
import { render } from '@testing-library/react';
import Wrapper from '@plone/volto/storybook';

export function renderInVolto(
  ui: React.ReactElement,
  customStore: Record<string, unknown> = {},
) {
  return render(
    <Wrapper anonymous customStore={customStore}>
      {ui}
    </Wrapper>,
  );
}
