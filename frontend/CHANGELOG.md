# Changelog

<!-- You should *NOT* be adding new change log entries to this file.
     You should create a file in the news directory instead.
     For helpful instructions, please see:
     https://6.docs.plone.org/contributing/index.html#contributing-change-log-label
-->

<!-- towncrier release notes start -->

## 3.0.0-alpha.1 (2026-10-05)


### Feature

- Showed the options of a poll that is not open yet, without the vote button. A closed poll still shows its results. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Added a Poll block that shows the latest open poll of the site section, or a chosen one, in any page: the voting portlet of 2.x, rebuilt as a block. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Shuffled the options of polls that ask for it, once per page view. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Allowed the Poll block inside a Grid block, and added an icon for the Poll content type. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Added a view for polls: voters choose an option and vote, then see the partial or final results as a bar chart, a pie chart or a table. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Added multiple choice polls: voters tick up to the number of options the poll allows. The form shows the poll's legend, or "Select one option" / "Select up to n options" when it has none. A multiple choice poll set to a pie chart shows a bar chart, since its shares do not add up to 100%. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Added a widget to edit the options of a poll: add, remove and reorder them, keeping the votes of each option. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- Added translations into Catalan, Czech, Dutch, Finnish, French, German, Spanish and Traditional Chinese, carried over from 2.x, and a complete Brazilian Portuguese translation. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
- The component that displays a poll, and the component that draws each graph type, can be replaced through the component registry, as `Poll` and `PollResultsGraph`. @ericof [#139](https://github.com/collective/collective.polls/issues/139)
