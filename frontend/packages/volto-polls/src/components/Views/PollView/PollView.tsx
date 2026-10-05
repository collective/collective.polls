import React from 'react';
import config from '@plone/volto/registry';
import { locatePoll } from '../../../helpers/components';
import { pollPath } from '../../../helpers/url';
import type { PollContent } from '../../../types/poll';

export interface PollViewProps {
  content: PollContent;
}

/**
 * The view of a poll: its title and description, then the poll itself.
 *
 * The poll is displayed by the component registered as `Poll`, the same
 * one the poll block uses.
 */
export const PollView = ({ content }: PollViewProps) => {
  const Container = config.getComponent?.({ name: 'Container' })?.component as
    | React.ElementType
    | undefined;
  const PollComponent = locatePoll();
  const body = (
    <>
      <h1 className="documentFirstHeading">{content.title}</h1>
      {content.description && (
        <p className="documentDescription">{content.description}</p>
      )}
      <PollComponent
        path={pollPath(content['@id'])}
        fallbackOptions={content.options}
        fallbackMaxChoices={content.max_choices}
        fallbackLegend={content.legend}
      />
    </>
  );
  return Container ? (
    <Container id="page-document" className="view-wrapper poll-view">
      {body}
    </Container>
  ) : (
    <div id="page-document" className="ui container view-wrapper poll-view">
      {body}
    </div>
  );
};

export default PollView;
