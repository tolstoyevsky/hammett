"""The module contains the tests for the screens."""

# ruff: noqa: ANN201

from hammett.core.constants import DEFAULT_STATE
from hammett.core.exceptions import ScreenDescriptionIsEmpty
from hammett.core.screen import Screen
from hammett.test.base import BaseTestCase
from tests.base import TestScreen


class TestScreenWithoutDescription(Screen):
    """The class implements a screen without a description."""


class ScreenTests(BaseTestCase):
    """The class implements the tests for the screens."""

    async def test_screen_without_description(self):
        """Test the case when a description of a screen is empty."""
        screen = TestScreenWithoutDescription()
        with self.assertRaises(ScreenDescriptionIsEmpty):
            await screen.move(self.update, self.context)

    async def test_send_handler(self):
        """Test the `send` handler of a screen."""
        screen = TestScreen()
        state = await screen.send(self.context)

        self.assertEqual(state, DEFAULT_STATE)
