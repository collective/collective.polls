from plone.base.interfaces.installable import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self) -> list[str]:
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "collective.polls:uninstall",
        ]

    def getNonInstallableProducts(self) -> list[str]:
        """Hide the upgrades package from site-creation and quickinstaller."""
        return [
            "collective.polls.upgrades",
        ]
