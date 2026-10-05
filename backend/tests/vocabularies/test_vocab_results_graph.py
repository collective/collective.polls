from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import pytest


class TestVocabResultsGraph:
    name: str = "collective.polls.ResultsGraph"

    @pytest.fixture(autouse=True)
    def _setup(self, portal, get_vocabulary) -> None:
        self.vocab = get_vocabulary(self.name, portal)

    def test_vocabulary_type(self):
        assert isinstance(self.vocab, SimpleVocabulary)

    def test_order(self):
        assert [term.token for term in self.vocab] == ["bar", "pie", "numbers"]

    @pytest.mark.parametrize(
        "token,title",
        [
            ("bar", "Bar Chart"),
            ("pie", "Pie Chart"),
            ("numbers", "Numbers Only"),
        ],
    )
    def test_vocab_terms(self, token: str, title: str):
        term = self.vocab.getTermByToken(token)
        assert isinstance(term, SimpleTerm)
        assert term.value == token
        assert term.title == title
