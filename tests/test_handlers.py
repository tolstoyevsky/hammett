"""The module contains the tests for the handlers."""

from typing import TYPE_CHECKING, cast

from hammett.core.constants import DEFAULT_STATE
from hammett.core.exceptions import CommandNameIsEmpty
from hammett.core.handlers import (
    _clear_command_name,
    _get_handler_name,
    calc_checksum,
    register_button_handler,
    register_command_handler,
)
from hammett.core.screen import Screen
from hammett.test.base import BaseTestCase
from tests.base import BaseTestScreenWithHandler

if TYPE_CHECKING:
    from hammett.types import Handler

_TEST_BUTTON_NAME = 'Test button'

_UNSUPPORTED_TYPE_VALUE = 1


class TestScreenWithHandler(BaseTestScreenWithHandler):
    """The class implements a screen with a handler."""


class TestScreenWithStaticHandler(Screen):
    """The class implements a screen with a static handler."""

    @staticmethod
    @register_button_handler
    async def handler(_update, _context):
        """Represent a stub handler for the testing purposes."""
        return DEFAULT_STATE


class HandlersTests(BaseTestCase):
    """The class implements the tests for the handlers."""

    def test_clearing_passed_command_name(self):
        """Test clearing a passed command name."""
        self.assertEqual('test', _clear_command_name('/test'))

    def test_getting_handler_name(self):
        """Test getting a handler name."""
        screen = TestScreenWithHandler()
        handler = cast('Handler', screen.handler)

        handler_name = _get_handler_name(handler)
        self.assertEqual('TestScreenWithHandler.handler', handler_name)

    def test_getting_static_handler_name(self):
        """Test getting a static handler name."""
        screen = TestScreenWithStaticHandler()
        handler = cast('Handler', screen.handler)

        handler_name = _get_handler_name(handler)
        self.assertEqual('TestScreenWithStaticHandler.handler', handler_name)

    def test_registering_command_handler_without_specified_command_name(self):
        """Test registering a command handler without specified command name."""
        with self.assertRaises(CommandNameIsEmpty):
            class TestScreenWithCommandHandler(Screen):
                """The class implements a screen without description
                a screen for this test.
                """

                @register_command_handler('')
                async def handler(self, _update, _context):
                    """Represent a stub handler for the testing purposes."""
                    return DEFAULT_STATE

    def test_passing_unsupported_type_to_calc_checksum(self):
        """Test passing an unsupported type to the calc_checksum function."""
        with self.assertRaises(TypeError):
            calc_checksum(_UNSUPPORTED_TYPE_VALUE)
