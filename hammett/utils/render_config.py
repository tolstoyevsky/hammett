"""The module contains helpers for working with RenderConfig."""

# ruff: noqa: SLF001

from typing import TYPE_CHECKING

from hammett.core.constants import LATEST_SENT_MSG_KEY, WIDGET_STATES_TO_CLEAN
from hammett.core.exceptions import MissingPersistence

if TYPE_CHECKING:
    from telegram import Message
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD

    from hammett.core.constants import FinalRenderConfig, LatestMessage


def _set_widget_state_to_clean(latest_msg: 'LatestMessage', user_data: 'UD') -> None:
    """Set a widget state to the user_data."""
    widget_state_to_clean = latest_msg['widget_state_key']
    if widget_state_to_clean:
        widget_states_to_clean = user_data.get(WIDGET_STATES_TO_CLEAN)  # type: ignore[attr-defined]
        if widget_states_to_clean:
            # Using of set here is impossible, since it is not JSON serializable
            if widget_state_to_clean not in widget_states_to_clean:
                user_data[WIDGET_STATES_TO_CLEAN].append(widget_state_to_clean)  # type: ignore[index]
        else:
            user_data[WIDGET_STATES_TO_CLEAN] = [widget_state_to_clean]  # type: ignore[index]


def get_latest_message(
    context: 'CallbackContext[BT, UD, CD, BD]',
    message: 'Message',
) -> 'LatestMessage | None':
    """Return the latest sent message info."""
    state: LatestMessage | None = None
    try:
        state = context.user_data[LATEST_SENT_MSG_KEY]  # type: ignore[index]
    except KeyError:
        pass
    except TypeError:
        if context._application.persistence:
            try:
                user_data = context._application.user_data[message.chat_id]
                state = user_data[LATEST_SENT_MSG_KEY]  # type: ignore[index]
            except KeyError:
                pass

    return state


async def save_latest_message(
    context: 'CallbackContext[BT, UD, CD, BD]',
    config: 'FinalRenderConfig',
    message: 'Message',
    widget_state_key: str,
) -> None:
    """Save the latest message info."""
    latest_msg: LatestMessage = {
        'hide_keyboard': config.hide_keyboard,
        'message_id': message.message_id,
        'chat_id': message.chat_id,
        'widget_state_key': widget_state_key,
    }
    try:
        last_sent_msg_key = context.user_data.get(LATEST_SENT_MSG_KEY)  # type: ignore[union-attr]
        if last_sent_msg_key:
            _set_widget_state_to_clean(last_sent_msg_key, context.user_data)

        context.user_data[LATEST_SENT_MSG_KEY] = latest_msg  # type: ignore[index]
    except AttributeError as exc:
        if not context._application.persistence:
            msg = (
                "It's not possible to pass data to user_data. "
                f"To solve the issue either don't use {save_latest_message.__name__} in jobs "
                f"or configure persistence."
            )
            raise MissingPersistence(msg) from exc

        user_data = context._application.user_data[message.chat_id]
        _set_widget_state_to_clean(latest_msg, user_data)

        user_data.update({  # type: ignore[attr-defined]
            LATEST_SENT_MSG_KEY: latest_msg,
        })

        await context._application.persistence.update_user_data(
            message.chat_id,
            user_data,
        )
