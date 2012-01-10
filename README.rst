**************************************************************
collective.polls
**************************************************************

.. contents:: Table of Contents
   :depth: 2


Overview
--------

A content type, workflow, and portlet for conducting online polls, for
anonymous and logged-in users.


Requirements
------------

    * Plone >= 4.1.x (http://plone.org/products/plone)

    * Dexterity >= 1.1 (http://plone.org/products/dexterity)
      Note: you may need to use known good versions of eggs for Dexterity; see http://plone.org/products/dexterity/documentation/how-to/install

Features
--------

    * Polls can be open for anonymous users to vote

    * Voting can take place in the object or in a voting portlet

    * The voting portlet shows automatically the latest open poll or a
      specific open poll

    * Users can see partial results of the poll

    * Results can be shown using a bar chart, a pie chart, or just by number
      of votes


Workflow description
--------------------

The workflow associated with polls has the following states: Private, Pending
review, Open and Closed.

    * Polls are created in Private state; only Owner, Manager, Editor or Site
      Administrator roles can modify them

    * When a poll is Private it can be sent to Pending review or directly to
      Open, if the user has the proper role

    * When a poll is Pending review it can be edited by Manager, Reviewer or
      Site Administrator roles

    * A poll in Pending review can be sent to Open, with "Review portal
      content" permission, or to Private, with "Request review" permission

    * When the poll is Open, people can only vote; nobody can modify the poll
      in any way

    * An Open poll can be sent to Private or Closed state by Manager or Site
      Administrator roles

    * When a poll is Closed nobody can modify it, nor can anyone vote on it; there
      is no way to reopen a closed poll
