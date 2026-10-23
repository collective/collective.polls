"""When an open poll shows its partial results."""

from collective.polls import _
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


#: Nobody but reviewers sees results until the poll closes.
NEVER = "never"

#: People who voted see the results.
AFTER_VOTE = "after_vote"

#: Everyone who can see the poll sees the results, voted or not.
ALWAYS = "always"

#: Token and title of each choice, in display order.
CHOICES: tuple[tuple[str, str], ...] = (
    (NEVER, _("Only when the poll is closed")),
    (AFTER_VOTE, _("After voting")),
    (ALWAYS, _("Always, even before voting")),
)


def show_results_choice(value: object) -> str:
    """Read the ``show_results`` of a poll as one of the choices.

    Polls saved before 3.0.0a2 hold a Bool: ``True`` showed the results
    after voting, ``False`` never did.

    :param value: The stored value.
    :returns: :data:`NEVER`, :data:`AFTER_VOTE` or :data:`ALWAYS`;
        :data:`AFTER_VOTE`, the default, for anything else.
    """
    if value is False:
        return NEVER
    if value in (NEVER, ALWAYS):
        return str(value)
    return AFTER_VOTE


# plone-stubs types provider() as a class decorator only; zope.interface
# accepts any object, and vocabulary factories are plain functions.
@provider(IVocabularyFactory)  # type: ignore[type-var]
def show_results_vocabulary(context: object) -> SimpleVocabulary:
    """Vocabulary of when an open poll shows its partial results.

    :param context: Context the vocabulary is looked up on. Unused: the
        choices are the same everywhere.
    :returns: One term per choice.
    """
    return SimpleVocabulary([
        SimpleTerm(value=value, token=value, title=title) for value, title in CHOICES
    ])
