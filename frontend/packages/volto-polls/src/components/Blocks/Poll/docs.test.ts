import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createIntl } from 'react-intl';
import type { JSONSchema } from '@plone/types';
import PollBlockInfo from './index';

const blocksDir = path.dirname(fileURLToPath(import.meta.url));

const FRONTMATTER = /^---\n([\s\S]*?)\n---\n/;

/** Split a `*.block.md` file into its frontmatter and its Markdown. */
function readDocs() {
  const file = readFileSync(path.join(blocksDir, 'docs.block.md'), 'utf8');
  return {
    frontmatter: file.match(FRONTMATTER)?.[1] ?? '',
    markdown: file.replace(FRONTMATTER, '').trim(),
  };
}

/** Resolve the block's schema with the arguments `@blocks-schema` passes. */
function resolveSchema(): JSONSchema {
  const intl = createIntl({ locale: 'en', messages: {}, onError: () => {} });
  const data = { '@type': PollBlockInfo.id };
  return (PollBlockInfo.blockSchema as (args: unknown) => JSONSchema)({
    data,
    intl,
    props: { data },
  });
}

const { frontmatter, markdown } = readDocs();
const schema = resolveSchema();
const examples = [...markdown.matchAll(/```json\n([\s\S]*?)\n```/g)].map(
  ([, json]) => JSON.parse(json),
);

describe('poll block docs', () => {
  it('names the block by the id the registry keys it by', () => {
    expect(PollBlockInfo.id).toBe('poll');
    expect(frontmatter).toBe(`block: ${PollBlockInfo.id}`);
  });

  it('opens with a one-paragraph summary', () => {
    expect(markdown.split(/\n\s*\n/)[0]).toMatch(/^Shows a poll /);
  });

  it('nests its headings below the one the endpoint adds', () => {
    expect(markdown).not.toMatch(/^#{1,2} /m);
  });

  it('explains every field of the schema', () => {
    for (const field of Object.keys(schema.properties ?? {})) {
      expect(markdown).toContain(`- \`${field}\`: `);
    }
  });

  it('has a minimal example and one using every field', () => {
    expect(examples).toContainEqual({ '@type': PollBlockInfo.id });
    expect(examples.flatMap(Object.keys)).toEqual(
      expect.arrayContaining(Object.keys(schema.properties ?? {})),
    );
  });

  it('only has examples that are data for this block', () => {
    const known = ['@type', ...Object.keys(schema.properties ?? {})];
    for (const example of examples) {
      expect(example['@type']).toBe(PollBlockInfo.id);
      expect(known).toEqual(expect.arrayContaining(Object.keys(example)));
    }
  });

  it('says what the block does not store', () => {
    expect(markdown).toContain('### Not stored in the block');
  });
});
