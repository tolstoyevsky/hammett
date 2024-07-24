"""The module is a script to run the bot."""

from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE

from demos.carousel.screens import MainMenu


def main():
    """Run the bot."""
    name = 'carousel'
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
