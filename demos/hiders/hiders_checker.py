"""The module contains the hiders checker for the bot. """

from hammett.conf import settings
from hammett.core.hider import HidersChecker


class DemoHidersChecker(HidersChecker):
    """The class implements the DemoHidersChecker hider checker."""

    async def is_admin(self, update, _context) -> bool:
        """Check whether the user is an admin."""
        user = update.effective_user
        return user.id in settings.ADMIN_GROUP
