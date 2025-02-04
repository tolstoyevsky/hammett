"""The module is a script for running the bot."""

from hammett.core import Application, Button
from hammett.core.constants import DEFAULT_STATE, RenderConfig, SourcesTypes
from hammett.core.handlers import register_button_handler
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence

MAIN_MENU_SCREEN_DESCRIPTION = (
    'Welcome to HammettDynamicKeyboard!\n'
    '\n'
    'Just press any button.'
)

MAIN_MENU_SCREEN_WITH_BUTTON_NUM_DESCRIPTION = (
    "You've pressed button number {button_num}, I'm right?"
)


def request_dynamic_keyboard(handler):
    """Emulate an API request, pass the description for the screen as a payload
    and return the built keyboard.
    """
    buttons = range(3)  # do some API request

    return [
        [Button(
            f'Button {button_num + 1}',
            handler,
            source_type=SourcesTypes.HANDLER_SOURCE_TYPE,
            payload=MAIN_MENU_SCREEN_WITH_BUTTON_NUM_DESCRIPTION.format(button_num=button_num + 1),
        )]
        for button_num in buttons
    ]


class MainMenuScreen(StartMixin):
    """The class implements MainMenuScreen."""

    description = MAIN_MENU_SCREEN_DESCRIPTION

    async def add_default_keyboard(self, _update, _context):
        """Set up the default keyboard for the screen."""
        return request_dynamic_keyboard(self.handle_button_click)

    @register_button_handler
    async def handle_button_click(self, update, context):
        """Handle a button click by getting text from the payload and
        passing it as a new description of the screen.
        """
        payload = await self.get_payload(update, context)

        await self.render(update, context, config=RenderConfig(description=payload))
        return DEFAULT_STATE


def main():
    """Run the bot."""
    app = Application(
        'HammettDynamicKeyboard',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {MainMenuScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()
