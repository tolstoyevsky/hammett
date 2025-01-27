"""The module is a script for running the bot."""

from hammett.core import Application, Screen
from hammett.core.constants import DEFAULT_STATE
from hammett.core.handlers import register_command_handler
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence

HELLO_SCREEN_DESCRIPTION = (
    'Hello 👋\n'
    'Now you see <b>HelloScreen</b>.'
)

START_SCREEN_DESCRIPTION = (
    'Welcome to HammettSimpleJumpBot!\n'
    '\n'
    'This is <b>StartScreen</b>, which acts as a response to the /start command. '
    'Now execute the /say_hello command, please.'
)


class HelloScreen(Screen):
    """The class implements HelloScreen, which acts as a response
    to the /say_hello command.
    """

    description = HELLO_SCREEN_DESCRIPTION

    @register_command_handler('say_hello')
    async def handle_typing_say_hello_command(self, update, context):
        """Send HelloScreen as a response to the /say_hello command."""
        return await self.jump(update, context)


class StartScreen(StartMixin):
    """The class implements StartScreen, which acts as a response
    to the /start command.
    """

    description = START_SCREEN_DESCRIPTION


def main():
    """Run the bot."""
    app = Application(
        'HammettSayHelloBot',
        entry_point=StartScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {HelloScreen, StartScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()
