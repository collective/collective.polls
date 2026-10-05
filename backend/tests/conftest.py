import os


# Compile the .po catalogs when the test layers load, as production images
# do: .mo files are not in the repository, and without them every message
# stays in English.
os.environ.setdefault("zope_i18n_compile_mo_files", "true")

from collective.polls.testing import ACCEPTANCE_TESTING
from collective.polls.testing import FUNCTIONAL_TESTING
from collective.polls.testing import INTEGRATION_TESTING
from pytest_plone import fixtures_factory


pytest_plugins = ["pytest_plone"]


globals().update(
    fixtures_factory((
        (ACCEPTANCE_TESTING, "acceptance"),
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)
