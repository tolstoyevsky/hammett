# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""The module contains the base class for the tests for
both Hammett itself and the bots based on the framework.
"""

import asyncio
import difflib
import pprint
import unittest
from dataclasses import asdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from unittest.util import _common_shorten_repr

from asgiref.sync import async_to_sync
from telegram import Bot, Chat, Message, Update, User
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram.constants import ChatType
from telegram.ext import Application, ApplicationBuilder, CallbackContext

from hammett.conf import settings
from hammett.core.constants import FinalRenderConfig, RenderConfig

if TYPE_CHECKING:
    from telegram._utils.types import JSONDict, ODVInput
    from typing_extensions import Self


class TestBot(Bot):
    """Class that represents a bot for testing purposes."""

    async def _do_post(
        self: 'Self',
        endpoint: str,  # noqa: ARG002
        data: 'JSONDict',  # noqa: ARG002
        *,
        read_timeout: 'ODVInput[float]' = DEFAULT_NONE,  # noqa: ARG002
        write_timeout: 'ODVInput[float]' = DEFAULT_NONE,  # noqa: ARG002
        connect_timeout: 'ODVInput[float]' = DEFAULT_NONE,  # noqa: ARG002
        pool_timeout: 'ODVInput[float]' = DEFAULT_NONE,  # noqa: ARG002
    ) -> 'bool | JSONDict | list[JSONDict]':
        """Override the method not to send any request."""
        return {
            'message_id': 1,
            'from_user': 1,
            'date': datetime.now(timezone.utc).timestamp(),
        }


class BaseTestCase(unittest.TestCase):
    """The class that subclasses unittest.TestCase to make it
    familiar with the specifics of the framework.
    """

    update: 'Update'
    context: 'CallbackContext'  # type: ignore[type-arg]

    def __init__(self: 'Self', method_name: str) -> None:
        """Initialize a base test case object."""
        naive_application = (
            ApplicationBuilder().bot(
                TestBot(token=settings.TOKEN),
            ).concurrent_updates(
                concurrent_updates=False,
            ).application_class(Application).build()
        )
        chat_id = 1
        self.chat = Chat(chat_id, ChatType.PRIVATE)

        self.context = CallbackContext(naive_application, chat_id=chat_id)

        self.user = User(1, 'TestUser', is_bot=False)
        self.message = Message(1, datetime.now(tz=timezone.utc), self.chat, from_user=self.user)
        self.update = Update(1, message=self.message)

        super().__init__(method_name)

    def __call__(self: 'Self', result: 'unittest.result.TestResult | None' = None) -> None:
        """Override __call__ to wrap asynchronous tests."""
        test_method = getattr(self, self._testMethodName)
        if asyncio.iscoroutinefunction(test_method):
            setattr(self, self._testMethodName, async_to_sync(test_method))

        super().__call__(result)

    def prepare_final_render_config(
        self,
        config: 'RenderConfig | FinalRenderConfig',
    ) -> 'FinalRenderConfig':
        """Transform `FinalRenderConfig` from `RenderConfig` if `RenderConfig` is provided,
        and pass the chat id to `FinalRenderConfig` for future assertions in tests.
        """
        if not isinstance(config, FinalRenderConfig):
            # The default keyboard needs to be replaced when casting to FinalRenderConfig.
            if config.keyboard is None:
                config.keyboard = []

            config = FinalRenderConfig(**asdict(config))

        config.chat_id = self.chat.id
        return config

    def assertFinalRenderConfigEqual(  # noqa: N802
        self,
        expected: 'FinalRenderConfig',
        actual: 'FinalRenderConfig',
        msg: str | None = None,
    ) -> None:
        """Compare two FinalRenderConfig objects."""
        self.assertIsInstance(
            expected, FinalRenderConfig, 'First argument is not a FinalRenderConfig',
        )
        self.assertIsInstance(
            actual, FinalRenderConfig, 'Second argument is not a FinalRenderConfig',
        )

        if expected != actual:
            first_config_repr, second_config_repr = _common_shorten_repr(
                expected, actual,  # type: ignore[arg-type]
            )

            standard_msg = f'{first_config_repr} != {second_config_repr}'
            diff = '\n' + '\n'.join(difflib.ndiff(
                pprint.pformat(expected).splitlines(),
                pprint.pformat(actual).splitlines(),
            ))

            standard_msg = self._truncateMessage(standard_msg, diff)  # type: ignore[attr-defined]

            self.fail(self._formatMessage(msg, standard_msg))
