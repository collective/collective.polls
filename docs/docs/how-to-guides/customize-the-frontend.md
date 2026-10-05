---
myst:
  html_meta:
    "description": "Replace how a poll or its results are displayed, through Volto's component registry."
    "property=og:description": "Replace how a poll or its results are displayed, through Volto's component registry."
    "property=og:title": "Customize the frontend"
    "keywords": "Plone, Volto, polls, customize, component registry, chart"
---

# Customize the frontend

The Volto add-on registers its main pieces in the component registry.
Your project or add-on can replace them from its configuration, without shadowing any file.

## Replace a results chart

The results of a poll are drawn by the component registered as `PollResultsGraph`, with the poll's graph type as the dependency: `bar`, `pie`, or `numbers`.
Each one receives the results, in the order of the poll's options.

```tsx
import type { PollResult } from '@plone-collective/volto-polls/src/types/poll';

export const MyBars = ({ results }: { results: PollResult[] }) => (
  <ul className="my-bars">
    {results.map((result) => (
      <li key={result.option_id}>
        {result.description}: {Math.round(result.percentage * 100)}%
      </li>
    ))}
  </ul>
);
```

Register it in your add-on's configuration function.

```ts
import { MyBars } from './components/MyBars';

export default function applyConfig(config) {
  config.registerComponent({
    name: 'PollResultsGraph',
    dependencies: ['bar'],
    component: MyBars,
  });
  return config;
}
```

Your add-on must come after `@plone-collective/volto-polls` in the `addons` list, so that its registration wins.

A multiple choice poll set to a pie chart is drawn with the `bar` component, because its percentages add up to more than 100.

## Replace the whole poll

The poll view and the Poll block both display a poll with the component registered as `Poll`.
Register your own to change both at once.

```ts
config.registerComponent({ name: 'Poll', component: MyPoll });
```

See {doc}`/reference/frontend` for the properties it receives.
