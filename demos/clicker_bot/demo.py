"""The module is a script for running the bot."""

from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence

CLICKER_SCREEN_DESCRIPTION = (
    'Welcome to HammettClickerBot! Click the button below, please.\n'
    '\n'
    'Current number of button clicks: <b>{num}</b>'
)


class ClickerScreen(StartMixin):
    """The class implements ClickerScreen, which acts as a response
    to the /start command.
    """

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return [[
            Button(
                '➕ 1',  # noqa: RUF001
                self.add_one_click,
                source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
            ),
        ]]

    @register_button_handler
    async def add_one_click(self, update, context):
        """Add one click to the click counter and re-render the screen."""
        context.user_data['clicks_num'] += 1

        return await self.move(update, context)

    async def get_description(self, _update, context):
        """Return a dynamic description."""
        return CLICKER_SCREEN_DESCRIPTION.format(num=context.user_data['clicks_num'])

    async def start(self, update, context):
        """Handle the /start command and initiate or reset the click counter."""
        context.user_data['clicks_num'] = 0

        return await super().start(update, context)


def main():
    """Run the bot."""
    app = Application(
        'HammettClickerBot',
        entry_point=ClickerScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {ClickerScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()
