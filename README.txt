****************
collective.polls
****************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

A content type, workflow, and portlet for conducting online polls, for
anonymous and logged-in users.

Don't Panic
-----------

TBA.

Features
^^^^^^^^

- Polls can be opened for anonymous users to vote
- If a open poll, allowed for anonymous is in a private folder nobody can vote.
  The parent folder of this poll should be published before opening the poll for
  this field to take effect
- Voting can take place in the object or in a voting portlet
- The voting portlet shows automatically the latest open poll or a specific
  open poll and closed polls
- Users can see partial results of the poll
- Results can be shown using a bar chart, a pie chart, or just by number of
  votes
- Polls can have relations with other content in the site

Workflow description
^^^^^^^^^^^^^^^^^^^^

The workflow associated with polls has the following states: Private, Pending
review, Open and Closed.

- Polls are created in Private state; only Owner, Manager, Editor or Site
  Administrator roles can modify them
- When a poll is Private it can be sent to Pending review or directly to Open,
  if the user has the proper role (Reviewer, Manager, Site Administrator)
- When a poll is Pending review it can be edited by Manager, Editor, Reviewer
  or Site Administrator roles
- A poll in Pending review can be sent to Open, with "Review portal content"
  permission, or to Private, with "Request review" permission
- When the poll is Open, people can only vote; nobody can modify the poll in
  any way
- An Open poll can be sent to Private or Closed state by Reviewer, Manager or
  Site Administrator roles
- When an Open poll is sent to Private, all votes are removed to avoid data
  manipulation.
- When a poll is Closed nobody can modify it, nor can anyone vote on it; there
  is no way to reopen a closed poll

Mostly Harmless
---------------

.. image:: https://secure.travis-ci.org/collective/collective.polls.png
    :target: http://travis-ci.org/collective/collective.polls

Have an idea? Found a bug? Let us know by `opening a support ticket`_.

.. _`opening a support ticket`: https://github.com/collective/collective.polls/issues

