"""The module is a script for running the bot."""

from hammett.conf import settings
from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE
from hammett.core.mixins import StartMixin
from hammett.core.persistence import RedisPersistence
from hammett.widgets import CarouselWidget

MAIN_MENU_SCREEN_FIRST_DESCRIPTION = (
    'Welcome to HammettCarouselBot!\n'
    '\n'
    'This is the first image in the carousel. To see the next one or the previous one, '
    'use the arrows below to navigate between images 👇.'
)

MAIN_MENU_SCREEN_LAST_DESCRIPTION = (
    "This is the end of the carousel screen.\n"
    "\n"
    "Here's the Hammett homepage: https://github.com/cusdeb-com/hammett"
)

MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION = (
    'Take part in Open Source and become a superhero🕷🕸 in software development!'
)


class MainMenuScreen(CarouselWidget, StartMixin):
    """The class implements MainMenuScreen."""

    cache_covers = True
    images = [
        [settings.MEDIA_ROOT / '01.jpg', MAIN_MENU_SCREEN_FIRST_DESCRIPTION],
        [settings.MEDIA_ROOT / '02.jpg', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '03.jpg', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '04.jpg', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '05.jpg', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '06.jpg', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '07.jpg', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '08.jpg', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '09.jpg', MAIN_MENU_SCREEN_MIDDLE_DESCRIPTION],
        [settings.MEDIA_ROOT / '10.jpg', MAIN_MENU_SCREEN_LAST_DESCRIPTION],
    ]


def main():
    """Run the bot."""
    app = Application(
        'HammettCarouselBot',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {MainMenuScreen},
        },
    )
    app.run()


if __name__ == '__main__':
    main()
