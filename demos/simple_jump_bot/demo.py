"""The module is a script for running the bot."""

from hammett.core import Application, Button, Screen
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence

NEXT_SCREEN_DESCRIPTION = (
    'Good job 😎\n'
    'Now you see <b>NextScreen</b>. It also has a button. After pressing it, '
    '<b>StartScreen</b> re-renders into <b>NextScreen</b>.'
)

START_SCREEN_DESCRIPTION = (
    'Welcome to HammettSimpleJumpBot!\n'
    '\n'
    'This is <b>StartScreen</b> and it is a response to the /start command. '
    'Click the button below to jump to <b>NextScreen</b>.'
)


class NextScreen(Screen):
    """The class implements NextScreen, which is always sent as a new message."""

    description = NEXT_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [[
            Button(
                '⬅️ Back',
                StartScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE,
            ),
        ]]


class StartScreen(StartMixin):
    """The class implements StartScreen, which acts as a response
    to the /start command.
    """

    description = START_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [[
            Button(
                'Next ➡️',
                NextScreen,
                source_type=SourcesTypes.JUMP_SOURCE_TYPE,
            ),
        ]]


def main():
    """Run the bot."""
    app = Application(
        'HammettSimpleJumpBot',
        entry_point=StartScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {NextScreen, StartScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()
