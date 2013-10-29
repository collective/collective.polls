****************
collective.polls
****************

.. contents:: Table of Contents

Life, the Universe, and Everything
----------------------------------

A content type, workflow and portlet for conducting online polls, for
anonymous and logged-in users.

Mostly Harmless
---------------

.. image:: https://secure.travis-ci.org/collective/collective.polls.png?branch=master
    :target: http://travis-ci.org/collective/collective.polls

.. image:: https://coveralls.io/repos/collective/collective.polls/badge.png?branch=master
    :target: https://coveralls.io/r/collective/collective.polls

Got an idea? Found a bug? Let us know by `opening a support ticket`_.

Don't Panic
-----------

Installation
^^^^^^^^^^^^

To enable this product in a buildout-based installation:

#. Edit your buildout.cfg and add ``collective.polls`` to the list of eggs to
   install::

    [buildout]
    ...
    eggs =
        collective.polls

#. If you are using Plone 4.1 you may need to extend a Dexterity known good
   set (KGS) to make sure that you get the right versions of the packages that
   make up Dexterity::

    [buildout]
    ...
    extends =
        https://good-py.appspot.com/release/dexterity/1.2.1?plone=4.1.6

After updating the configuration you need to run ''bin/buildout'', which will
take care of updating your system.

Go to the 'Site Setup' page in a Plone site and click on the 'Add-ons' link.

Check the box next to ''collective.polls'' and click the 'Activate' button.

.. Note::
    You may have to empty your browser cache and save your resource registries
    in order to see the effects of the product installation.

Features
^^^^^^^^

- Polls can be opened for anonymous users to vote;
- If an open poll is allowed for anonymous but is inside a private folder,
  nobody can vote. Therefore the poll's parent folder needs to be published
  before opening the poll in order for this field to take effect;
- Voting can take place either in the object or in a voting portlet;
- The voting portlet can show the latest open poll or ab specific open poll
  and closed polls;
- Users can see partial results of the poll;
- Results can be shown using a bar chart, a pie chart, or just by number of
  votes;
- Polls can have relations with other content in the site.

Workflow description
^^^^^^^^^^^^^^^^^^^^

The workflow associated with polls has the following states: Private, Pending
review, Open and Closed.

- Polls are created in Private state, so only Owner, Manager, Editor or Site
  Administrator roles can modify them);
- When a poll is Private it can be sent to Pending review or directly to Open
  state, if the user has the proper role (Reviewer, Manager, Site
  Administrator);
- When a poll is Pending review it can be edited by Manager, Editor, Reviewer
  or Site Administrator roles;
- A poll in Pending review can be sent to Open, with "Review portal content"
  permission, or to Private, with "Request review" permission;
- When the poll is Open people can only vote; nobody can modify the poll in
  any way;
- An Open poll can be sent to Private or Closed state by Reviewer, Manager or
  Site Administrator roles;
- When an Open poll is sent to Private, all votes are removed to avoid data
  manipulation;
- When a poll is Closed nobody can modify it, nor can anyone vote on it; there
  is no way to reopen a closed poll.

Not entirely unlike
-------------------

`Plone PoPoll`_
    A very old an unmaintained product, PoPoll includes a poll tool that
    allows member or anonymous to vote for one or more answers. A portlet is
    provided. It can be configured to display the last poll, or the first poll
    of a folder. After the vote statistics screens are shown.

.. _`opening a support ticket`: https://github.com/collective/collective.polls/issues
.. _`Plone PoPoll`: http://plone.org/products/plonepopoll
