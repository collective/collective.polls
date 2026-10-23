from collective.polls.vocabularies.show_results import show_results_choice
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import pytest


class TestVocabShowResults:
    name: str = "collective.polls.ShowResults"

    @pytest.fixture(autouse=True)
    def _setup(self, portal, get_vocabulary) -> None:
        self.vocab = get_vocabulary(self.name, portal)

    def test_vocabulary_type(self):
        assert isinstance(self.vocab, SimpleVocabulary)

    def test_order(self):
        assert [term.token for term in self.vocab] == [
            "never",
            "after_vote",
            "always",
        ]

    @pytest.mark.parametrize(
        "token,title",
        [
            ("never", "Only when the poll is closed"),
            ("after_vote", "After voting"),
            ("always", "Always, even before voting"),
        ],
    )
    def test_vocab_terms(self, token: str, title: str):
        term = self.vocab.getTermByToken(token)
        assert isinstance(term, SimpleTerm)
        assert term.value == token
        assert term.title == title


@pytest.mark.parametrize(
    "value,expected",
    [
        ("never", "never"),
        ("after_vote", "after_vote"),
        ("always", "always"),
        (True, "after_vote"),
        (False, "never"),
        (None, "after_vote"),
        ("unknown", "after_vote"),
    ],
)
def test_show_results_choice(value, expected):
    assert show_results_choice(value) == expected
