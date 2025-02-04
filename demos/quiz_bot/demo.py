"""The module is a script for running the bot."""

# ruff: noqa: I001

from hammett.core import Application
from hammett.core.constants import DEFAULT_STATE
from hammett.core.persistence import RedisPersistence

from screens import (
    LanguageSwitcherScreen,
    MainMenuScreen,
    QuizMultiChoiceWidget,
    QuizSingleChoiceWidget,
    ResultScreen,
)


def main():
    """Run the bot."""
    app = Application(
        'HammettQuizBot',
        entry_point=MainMenuScreen,
        persistence=RedisPersistence(),
        states={
            DEFAULT_STATE: {
                LanguageSwitcherScreen,
                MainMenuScreen,
                QuizMultiChoiceWidget,
                QuizSingleChoiceWidget,
                ResultScreen,
            },
        },
    )
    app.run()


if __name__ == '__main__':
    main()
