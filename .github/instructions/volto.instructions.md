---
name: "TypeScript and React Coding Standards"
description: "Standards and guidelines for TypeScript and React code in Volto projects."
applyTo: "**/*.ts,**/*.tsx"
---
# Project coding standards for TypeScript and React


## TypeScript Guidelines

- Use TypeScript for all new code
- Follow functional programming principles where possible
- Use interfaces for data structures and type definitions
- Prefer immutable data (const, readonly)
- Use optional chaining (?.) and nullish coalescing (??) operators

## React Guidelines

- Use functional components with hooks
- Follow the React hooks rules (no conditional hooks)
- Keep components small and focused

## Volto Guidelines

- Always check [Volto documentation](https://6.docs.plone.org/volto/index.html) for best practices
- Consider @plone/volto to be 18.x or later
- Use `@plone/components` for common UI elements, and check the available components at the [Plone Components Storybook](https://plone-components.readthedocs.io/latest/?path=/docs/introduction--docs)
- For typing information always refer to `@plone/types` package.
- Use Volto's built-in components and utilities when possible

## Internalization (i18n)

- All code variables and identifiers must be in English
- All UI strings must be translatable
- Use framework i18n tools properly
- No hardcoded text

## Loop Detection

- If repeating same pattern, STOP
- Reassess approach
- Check official documentation
- State: "We are in a loop, need different approach"


## No Shortcuts or Hacks

- Always use official APIs
- Follow framework best practices
- No temporary workarounds
- No "quick fixes"

## Violations

If human says any of these, you have violated rules:

- "Have you checked docs?"
- "Are you guessing?"
- "Did that work?"
- "Are we in a loop?"

## Success Metrics
- Commands execute without error
- Features work as specified
- System is maintainable
- Time invested yields results
- Human feels energized, not drained


## Failure Indicators
- Repeating same approaches
- Theoretical explanations without testing
- Claims of success without functionality
- Hours spent without progress
- Human dreading the next interaction
