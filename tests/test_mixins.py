"""The module contains the tests for the mixins."""

from hammett.core.constants import DEFAULT_STATE
from hammett.core.exceptions import ScreenRouteIsEmpty
from hammett.core.mixins import RouteMixin
from hammett.test.base import BaseTestCase
from tests.base import TestStartScreen


class TestRouteScreenWithoutRoutes(RouteMixin):
    """The class implements a screen without specified routes attribute."""


class MixinTests(BaseTestCase):
    """The class implements the tests for the mixins."""

    def test_route_screen_without_specified_routes(self):
        """Test the case when a routes attribute is not specified."""
        with self.assertRaises(ScreenRouteIsEmpty):
            TestRouteScreenWithoutRoutes()

    async def test_start_handler_of_start_mixin(self):
        """Test the case when the start method from StartMixin is used."""
        screen = TestStartScreen()
        state = await screen.start(self.update, self.context)

        self.assertEqual(DEFAULT_STATE, state)
