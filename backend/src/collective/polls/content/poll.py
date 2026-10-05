from collective.polls import _
from collective.polls.config import COOKIE_KEY
from collective.polls.config import MEMBERS_ANNO_KEY
from collective.polls.config import PERMISSION_VOTE
from collective.polls.config import VOTE_ANNO_KEY
from collective.polls.utility import IPolls
from plone import api
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zope.event import notify
from zope.interface import implementer
from zope.interface import Invalid
from zope.interface import invariant
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


graph_options = SimpleVocabulary([
    SimpleTerm(value="bar", title=_("Bar Chart")),
    SimpleTerm(value="pie", title=_("Pie Chart")),
    SimpleTerm(value="numbers", title=_("Numbers Only")),
])


class InsuficientOptions(Invalid):
    __doc__ = _("Not enought options provided")


# TODO: move to interfaces module
class IPoll(model.Schema):
    """A Poll in a Plone site."""

    allow_anonymous = schema.Bool(
        title=_("Allow anonymous"),
        description=_(
            "Allow not logged in users to vote. "
            "The parent folder of this poll should be published before opeining "
            "the poll for this field to take effect"
        ),
        default=True,
    )

    # multivalue = schema.Bool(
    #    title = _(u"Multivalue"),
    #    description = _(u"Voters can choose several answers at the same "
    #                     "time."),
    # )

    show_results = schema.Bool(
        title=_("Show partial results"),
        description=_("Show partial results after a voter has already voted."),
        default=True,
    )

    results_graph = schema.Choice(
        title=_("Graph"),
        description=_("Format to show the results."),
        default="bar",
        required=True,
        source=graph_options,
    )

    options = schema.List(
        title=_("Available options"),
        value_type=schema.TextLine(),
        default=[],
        required=True,
    )

    @invariant
    def validate_options(data):
        """Validate options."""
        options = data.options
        descriptions = options and list(options)
        if len(descriptions) < 2:
            raise InsuficientOptions(
                _("You need to provide at least two options for a poll.")
            )


@implementer(IPoll)
class Poll(Item):
    """A Poll in a Plone site."""

    __ac_permissions__ = ((PERMISSION_VOTE, ("setVote", "_setVoter")),)

    @property
    def annotations(self):
        return IAnnotations(self)

    @property
    def utility(self):
        utility = queryUtility(IPolls, name="collective.polls")
        return utility

    def getOptions(self):
        """Return available options."""
        options = self.options
        return options

    def _getVotes(self):
        """Return votes in a dict format."""
        votes = {"options": [], "total": 0}
        for option in self.getOptions():
            index = option.get("option_id")
            description = option.get("description")
            option_votes = self.annotations.get(VOTE_ANNO_KEY % index, 0)
            votes["options"].append({
                "description": description,
                "votes": option_votes,
                "percentage": 0.0,
            })
            votes["total"] = votes["total"] + option_votes
        for option in votes["options"]:
            if option["votes"]:
                option["percentage"] = option["votes"] / votes["total"]
        return votes

    def getResults(self):
        """Return results so far."""
        votes = self._getVotes()
        # Bars show wrong when there are no vote
        if votes["total"] == 0:
            return []
        all_results = []
        for item in votes["options"]:
            all_results.append((item["description"], item["votes"], item["percentage"]))
        return all_results

    def _validateVote(self, options=None):
        """Check if passed options are available here."""
        available_options = [o["option_id"] for o in self.getOptions()]
        if isinstance(options, list):
            # TODO: Allow multiple options
            # multivalue = self.multivalue
            return False
        else:
            return options in available_options

    def _setVoter(self, request=None):
        """Mark this user as a voter."""
        utility = self.utility
        annotations = self.annotations
        voters = self.voters()
        member = utility.member
        member_id = member.getId()
        if not member_id and request:
            cookie = COOKIE_KEY + api.content.get_uuid(self)
            expires = "Wed, 19 Feb 2020 14:28:00 GMT"  # XXX: why hardcoded?
            vote_id = str(utility.anonymous_vote_id())
            request.response[cookie] = vote_id
            request.response.setCookie(cookie, vote_id, path="/", expires=expires)
            member_id = "Anonymous-" + vote_id

        if member_id:
            voters.append(member_id)
            annotations[MEMBERS_ANNO_KEY] = voters
            return True

    def voters(self):
        annotations = self.annotations
        voters = annotations.get(MEMBERS_ANNO_KEY, [])
        return voters

    @property
    def total_votes(self):
        """Return the number of votes so far."""
        votes = self._getVotes()
        return votes["total"]

    def setVote(self, options=None, request=None):
        """Set a vote on this poll."""
        annotations = self.annotations
        utility = self.utility
        if not utility.allowed_to_vote(self, request):
            return False
        if not self._validateVote(options):
            return False
        if not isinstance(options, list):
            options = [options]
        if not self._setVoter(request):
            # We failed to set voter, so we will not compute its votes
            return False
        # set vote in annotation storage
        for option in options:
            vote_key = VOTE_ANNO_KEY % option
            votes = annotations.get(vote_key, 0)
            annotations[vote_key] = votes + 1
        notify(ObjectModifiedEvent(self))
        return True
