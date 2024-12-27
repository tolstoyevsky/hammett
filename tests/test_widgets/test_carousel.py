"""The module contains tests for the CarouselWidget."""

# ruff: noqa: SLF001

from fakeredis import FakeAsyncRedis
from telegram.ext import CallbackContext

from hammett.core.persistence import RedisPersistence
from hammett.test.base import BaseTestCase
from hammett.widgets.carousel_widget import CarouselWidget
from tests.base import (
    CHAT_ID,
    MESSAGE_ID,
    USER_ID,
    BaseTestScreenWithMockedRenderer,
)

_DATA = {'key1': 'value1', 'key2': 'value2'}


class BaseTestCarouselWidget(CarouselWidget, BaseTestScreenWithMockedRenderer):
    """The class implements the base CarouselWidget for the testing purposes."""

    images = [
        ['cover_1', 'description_1'],
        ['cover_2', 'description_2'],
    ]


class TestCarouselWidget(BaseTestCarouselWidget):
    """The class implements a screen based on CarouselWidget for the testing purposes."""


class CarouselWidgetTests(BaseTestCase):
    """The class implements the tests for CarouselWidget."""

    def get_context(self):
        """Return the `CallbackContext` object for testing purposes."""
        return CallbackContext(
            self.get_native_application(),
            chat_id=self.chat_id,
        )

    async def test_updating_user_data_after_sending_carousel_widget_as_notification(self):
        """Test updating the user_data when a screen based on CarouselWidget is sent
        as a notification.
        """
        self.context._application.persistence = RedisPersistence()
        self.context._application.persistence.redis_cli = FakeAsyncRedis()
        self.context._application.user_data = {USER_ID: _DATA}

        await TestCarouselWidget().send(self.context)

        updated_user_data = self.context._application.persistence.user_data
        state_key = await TestCarouselWidget()._get_state_key(
            chat_id=CHAT_ID,
            message_id=MESSAGE_ID,
        )
        self.assertEqual(updated_user_data, {
            USER_ID: {
                state_key: {'images': TestCarouselWidget().images},
                **_DATA,
            },
        })
