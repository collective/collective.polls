Changelog
---------

There's a frood who really knows where his towel is.

1.10b1 (2017-06-16)
^^^^^^^^^^^^^^^^^^^

.. Warning::
    This release removes collective.z3cform.widgets from the list of dependencies;
    so, it would be a good idea to add this package on the `eggs` part of your buildout configuration before upgrading to avoid ending with a broken dependency.
    After running the upgrade step you can safely uninstall collective.z3cform.widgets and remove it from your buildout configuration if you don't have any other add-on depending on it.

- Remove ExplorerCanvas script;
  this will break compatibility with IE8 and below butâŚ who cares?
  [hvelarde]

- Remove dependency on collective.z3cform.widgets.
  [sneridagh, hvelarde]

- Add Catalan translation.
  [sneridagh]

- Remove hard dependency on five.grok.
  [rodfersou, puittenbroek, hvelarde]

- Remove soft dependency on zope.formlib under Plone 5 (HT @ale-rt).
  [hvelarde]

- Do not fail while adding a portlet under Plone 5 (closes `#106`_).
  [hvelarde]


1.9b1 (2016-09-29)
^^^^^^^^^^^^^^^^^^

.. Warning::
    This release removes some packages from the list of dependencies.
    Be sure to read the whole changelog and apply the related changes to your buildout configuration while upgrading.
    Also, note that this is the first release marked as compatible with Plone 5;
    it still has some issues and must not be used in production with that version.

- Package is now compatible with Plone 5.0 and Plone 5.1.
  [hvelarde]

- Remove hard dependency on plone.app.referenceablebehavior as Archetypes is no longer the default framework in Plone 5.
  Under Plone < 5.0 you should now explicitly add it to the `eggs` part of your buildout configuration to avoid issues while upgrading.
  [hvelarde]

- Get rid of the ``uid_for_poll`` function.
  [hvelarde]

- Wrap poll choices with label-tag for easier option selection.
  [datakurre]

- Add Finnish translation.
  [datakurre]

- Add Traditional Chinese translation.
  [l34marr]


1.8.1 (2015-12-11)
^^^^^^^^^^^^^^^^^^

- The display of poll results was refactored to avoid issues with reverse proxies like Varnish;
  updates are now handled client-side using AJAX calls (closes `#96`_).
  [rodfersou]


1.8 (2015-11-24)
^^^^^^^^^^^^^^^^

- Add link to show partial results of an open poll (closes `#93`_).
  [rodfersou]

- Poll tile now displays the results of the poll after a vote has been cast (closes `#90`_).
  [rodfersou]


1.7 (2015-08-25)
^^^^^^^^^^^^^^^^^^

- Add Poll tile for collective.cover.
  [hvelarde]


1.6.2 (2015-03-11)
^^^^^^^^^^^^^^^^^^

- Add upgrade step to remove missing resource from JS registry (fixes `#83`_).
  [hvelarde]

- Update German translation.
  [mbaechtold]

- Added Czech translation
  [naro]


1.6.1 (2014-08-19)
^^^^^^^^^^^^^^^^^^

- Remove ``@@legendothers_translation.js`` because it is not used anywhere.
  [rafaelbco]


1.6 (2014-05-01)
^^^^^^^^^^^^^^^^

- Add a default value to the voting portlet ``poll`` parameter. This fixes an
  issue happening when importing ``portlets.xml`` assignments.
  [ericof]

- Remove unnecesary code in portlet (closes `#73`_).
  [nueces]

- In portlet link back to poll page (closes `#47`_).
  [marcosfromero]


1.5 (2013-12-17)
^^^^^^^^^^^^^^^^

- Make the add-on aware of subsites (INavigationRoot) [rafaelbco]

- Implement show_total for the portlet (closes `#64`_). [marcosfromero]

- Depend on plone.api.
  [hvelarde]

- Remove dependency on unittest2; package is not going to be tested under
  Python 2.6 anymore.
  [hvelarde]

- Drop support for Plone 4.1. [hvelarde]

- Add French translation. [toutpt]


1.4 (2013-04-10)
^^^^^^^^^^^^^^^^^^

- Tested for Plone 4.3 compatibility. [ericof, hvelarde]

- Anonymous voters can now vote again on a reopened poll (fixes `#35`_).
  [ericof]

- Remove cmf.ManagePortal permission when editing the portlets. [flecox]


1.3.1 (2013-03-27)
^^^^^^^^^^^^^^^^^^

- Fix refreshing the portlet.  Previously no html would be returned
  when the portlet was defined on a default page.  The refresh would
  fail with a ComponentLookupError when used inside a panel of
  collective.panels.
  [maurits]

- Fixing jQuery bug when doing AJAX call in portlet. [flecox]


1.3 (2013-01-14)
^^^^^^^^^^^^^^^^

- Test compatibility with Plone 4.3. [hvelarde]

- Bump up version of collective.z3cform.widgets dependency to 1.0b3.
  [hvelarde]

- Declare Pillow as a package dependency. [hvelarde]

- Add Dutch translation. [fredvd]

- Fixed permissions checks for anonymous users when a poll is at the
  root level of the site (fixes `#61`_). [vincentpsarga]


1.2 (2012-09-16)
^^^^^^^^^^^^^^^^

- EnhancedTextLinesFieldWidget widget was updated; new features (like inline
  editing and reordering) are now available. [hvelarde]

- Added the 'open' transition to the 'closed' state, that way, polls can be
  re-opened after they were closed (closes `#53`_). [frapell]


1.1 (2012-08-14)
^^^^^^^^^^^^^^^^^^

- Multiple poll charts can be rendered in one page. [Quimera]

- Multiple poll portlets can be rendered in one page. [Quimera]

- Updated Brazilian Portuguese translation. [rafahela]

- Add translation functionality for the 'Others' string and translate it to
  German. [eschmutz]

- Fixed translation strings for actions on poll workflow; updated Spanish and
  Brazilian Portuguese translations. [hvelarde]

- Update German translations. [tschanzt]

- allow_anonymous field is always shown (fixes `#51`_). [hvelarde]

- Some refactoring on tests was done; we now test for CSS installation and
  removal. [hvelarde]

- DataGridField widget was replaced with EnhancedTextLinesFieldWidget.
  [flecox, hvelarde]


1.0.1 (2012-05-08)
^^^^^^^^^^^^^^^^^^

- Fix UnicodeDecodeError in PossiblePolls vocabulary when we have a
  poll with umlauts in the title. [elioschmutz]

- Add German translation. [elioschmutz]


1.0 (2012-05-02)
^^^^^^^^^^^^^^^^

- Tested for Plone 4.2 compatibility. [hvelarde]

- Updated Dexterity version requirement (we want to use latest version to
  avoid any issues). [hvelarde]

- Added a nice hack to include both README.txt and README.rst in the package
  declaration. [hvelarde]

- Pie chart is now shown when all votes go to one option (issue #27). [flecox]


1.0rc2 (2012-02-20)
^^^^^^^^^^^^^^^^^^^

- Ajax load of partial results on portlet (issue #37). [Quimera]

- Updated Brazilian Portuguese translation. [ericof]

- Added option to control if portlet shows closed polls when no open ones are
  available (issue #32). [ericof]

- Added validation for Poll options (issue #31). [ericof]

- Add a subscriber to erase votes when poll is sent back to revision (issue
  #33). [ericof]

- Fix Anonymous permissions to View and Vote on polls. [ericof]

- Modify workflows and permissions to be consistent with the ones used in
  Plone. [ericof]

- Fixed MANIFEST.in file. [nueces]

- Renamed the workflow state to 'Opened' instead of 'Published' (issue #26).
  [frapell]

- Updated tests and translations. [frapell]

- Added the pieChart to the portlet (issue #23). [frapell]

- Made the poll redirect to the place where the vote was casted (issue #22).
  [frapell]

- Updated Spanish translation. [hvelarde]

- Fixed permissions on private and pending states (issue #20). [hvelarde]

- Fixed javascript registry uninstall and tests. [hvelarde]


1.0rc1 (2012-01-10)
^^^^^^^^^^^^^^^^^^^

- Initial release.

.. _`#35`: https://github.com/collective/collective.polls/issues/35
.. _`#47`: https://github.com/collective/collective.polls/issues/47
.. _`#51`: https://github.com/collective/collective.polls/issues/51
.. _`#53`: https://github.com/collective/collective.polls/issues/53
.. _`#61`: https://github.com/collective/collective.polls/issues/61
.. _`#64`: https://github.com/collective/collective.polls/issues/64
.. _`#73`: https://github.com/collective/collective.polls/issues/73
.. _`#83`: https://github.com/collective/collective.polls/issues/83
.. _`#90`: https://github.com/collective/collective.polls/issues/90
.. _`#93`: https://github.com/collective/collective.polls/issues/93
.. _`#96`: https://github.com/collective/collective.polls/issues/96
.. _`#106`: https://github.com/collective/collective.polls/issues/106
