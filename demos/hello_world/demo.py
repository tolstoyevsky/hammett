"""The module is a script to run the bot."""

from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.mixins import StartMixin
from hammett.core.screen import Screen


class HelloScreen(StartMixin, Screen):
    """The class implements the HelloScreen screen."""

    description = 'Hello, World!'

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [[
            Button(
                'Next screen ➡️',
                YetAnotherScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE,
            ),
        ]]


class YetAnotherScreen(StartMixin, Screen):
    """The class implements the YetAnotherScreen screen."""

    description = (
        'This is just another screen to demonstrate the built-in '
        'capability to switch between screens.'
    )

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [[
            Button(
                '⬅️ Back',
                HelloScreen,
                source_type=SourcesTypes.MOVE_SOURCE_TYPE,
            ),
        ]]


def main():
    """Runs the bot."""

    name = 'hello_world'
    app = Application(
        name,
        entry_point=HelloScreen,
        states={
            DEFAULT_STATE: [HelloScreen, YetAnotherScreen],
        },
    )
    app.run()


if __name__ == '__main__':
    main()
