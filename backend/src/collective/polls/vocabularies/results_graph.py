"""The formats a poll can show its results in."""

from collective.polls import _
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


#: Token and title of each format, in display order.
GRAPHS: tuple[tuple[str, str], ...] = (
    ("bar", _("Bar Chart")),
    ("pie", _("Pie Chart")),
    ("numbers", _("Numbers Only")),
)


# plone-stubs types provider() as a class decorator only; zope.interface
# accepts any object, and vocabulary factories are plain functions.
@provider(IVocabularyFactory)  # type: ignore[type-var]
def results_graph_vocabulary(context: object) -> SimpleVocabulary:
    """Vocabulary of the formats a poll can show its results in.

    :param context: Context the vocabulary is looked up on. Unused: the
        formats are the same everywhere.
    :returns: One term per format.
    """
    return SimpleVocabulary([
        SimpleTerm(value=value, token=value, title=title) for value, title in GRAPHS
    ])
