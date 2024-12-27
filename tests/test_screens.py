"""The module contains the tests for the screens."""

# ruff: noqa: S106, SLF001

from fakeredis import FakeAsyncRedis
from telegram.ext import CallbackContext

from hammett.core.constants import DEFAULT_STATE, LATEST_SENT_MSG_KEY
from hammett.core.exceptions import ScreenDescriptionIsEmpty
from hammett.core.persistence import RedisPersistence
from hammett.core.screen import Screen
from hammett.test.base import BaseTestCase
from hammett.test.utils import override_settings
from tests.base import (
    CHAT_ID,
    MESSAGE_ID,
    USER_ID,
    BaseTestScreenWithDescription,
    BaseTestScreenWithHideKeyboard,
    BaseTestScreenWithMockedRenderer,
    TestScreen,
)

_DATA = {'key1': 'value1', 'key2': 'value2'}


class TestScreenWithMockedRendererAndHideKeyboard(
    BaseTestScreenWithMockedRenderer,
    BaseTestScreenWithDescription,
    BaseTestScreenWithHideKeyboard,
):
    """The class represents the base screen for the testing purposes."""


class TestScreenWithoutDescription(Screen):
    """The class implements a screen without a description."""


class ScreenTests(BaseTestCase):
    """The class implements the tests for the screens."""

    def get_context(self):
        """Return the `CallbackContext` object for testing purposes."""
        return CallbackContext(
            self.get_native_application(),
            chat_id=self.chat_id,
        )

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

    @override_settings(SAVE_LATEST_MESSAGE=True, TOKEN='secret-token')
    async def test_updating_user_data_after_sending_notification_with_hiding_keyboard(self):
        """Test updating the user_data when a screen is sent as a notification
        with hiding keyboard.
        """
        self.context._application.persistence = RedisPersistence()
        self.context._application.persistence.redis_cli = FakeAsyncRedis()
        self.context._application.user_data = {USER_ID: _DATA}

        await TestScreenWithMockedRendererAndHideKeyboard().send(self.context)

        updated_user_data = self.context._application.persistence.user_data
        self.assertEqual(updated_user_data, {
            USER_ID: {
                LATEST_SENT_MSG_KEY: {
                    'hide_keyboard': True,
                    'message_id': MESSAGE_ID,
                    'chat_id': CHAT_ID,
                },
                **_DATA,
            },
        })
