"""The module is a script to run the bot."""

from demos.single_choices.screens import MainMenu
from hammett.core.application import Application
from hammett.core.constants import DEFAULT_STATE


def main():
    """Run the bot."""
    name = 'single_choice'
    app = Application(
        name,
        entry_point=MainMenu,
        states={
            DEFAULT_STATE: [MainMenu],
        },
    )
    app.run()


if __name__ == '__main__':
    main()
