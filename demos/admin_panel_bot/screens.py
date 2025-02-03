"""The module contains the screens the bot consists of."""

from hammett.conf import settings
from hammett.core import Button, Screen
from hammett.core.constants import SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.hider import ONLY_FOR_ADMIN, Hider
from hammett.core.mixins import StartMixin

ADMIN_PANEL_SCREEN_DESCRIPTION = (
    "This is <b>AdminPanelScreen</b>. You've managed to move here, "
    "because you could see the button that moves to this screen.\n"
    "\n"
    "Now remove yourself from the admin group to see what will change."
)

MAIN_MENU_SCREEN_DESCRIPTION = (
    "Welcome to HammettAdminPanelBot!\n"
    "\n"
    "This is <b>MainMenuScreen</b>, which actually contains <b>two</b> buttons. "
    "But only <b>one</b> of them is visible for the users who doesn't have the <i>admin</i> role."
)

NOT_ADMIN_CONFIRMATION_SCREEN_DESCRIPTION = (
    "Are you sure you want to remove yourself from the admin group?\n"
    "\n"
    "(Don't worry, you can get your privilege back right after typing "
    "the /start command 😉)"
)


class AdminPanelScreen(Screen):
    """The class implements AdminPanelScreen."""

    description = ADMIN_PANEL_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                "⚠️ I'm not an admin!",
                NotAdminConfirmationScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE,
                hiders=Hider(ONLY_FOR_ADMIN))],
            [Button('⬅️ Main Menu',
                    MainMenuScreen,
                    source_type=SourcesTypes.MOVE_SOURCE_TYPE,
                    hiders=Hider(ONLY_FOR_ADMIN))],
        ]


class MainMenuScreen(StartMixin, Screen):
    """The class implements MainMenuScreen."""

    description = MAIN_MENU_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                '👑 Admin Panel',
                AdminPanelScreen,
                hiders=Hider(ONLY_FOR_ADMIN),
                source_type=SourcesTypes.MOVE_SOURCE_TYPE)],
            [Button(
                '🎸 Hammett Home Page',
                'https://github.com/cusdeb-com/hammett',
                source_type=SourcesTypes.URL_SOURCE_TYPE)],
        ]

    async def start(self, update, context):
        """Handle the /start command and add the user to the admin group."""
        user = update.effective_user
        settings.ADMIN_GROUP.append(user.id)

        return await super().start(update, context)


class NotAdminConfirmationScreen(Screen):
    """The class implements NotAdminConfirmationScreen."""

    description = NOT_ADMIN_CONFIRMATION_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [
            [Button(
                '✅ Yes',
                self.exclude_from_admin_group,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
                hiders=Hider(ONLY_FOR_ADMIN))],
            [Button(
                '❌ No',
                MainMenuScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE,
                hiders=Hider(ONLY_FOR_ADMIN))],
        ]

    @register_button_handler
    async def exclude_from_admin_group(self, update, context):
        """Handle an excluding of the user from the admin group."""
        user = update.effective_user
        settings.ADMIN_GROUP.remove(user.id)

        return await MainMenuScreen().move(update, context)
