"""The module contains the implementation of the screen components
(i.e., cover, description and keyboard).
"""

import logging
import re
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from telegram._utils.defaultvalue import DEFAULT_NONE, DefaultValue
from telegram.constants import ParseMode

from hammett.core import handlers
from hammett.core.constants import (
    DEFAULT_STAGE,
    SourcesTypes,
)
from hammett.core.exceptions import (
    FailedToGetDataAttributeOfQuery,
    ImproperlyConfigured,
    PayloadIsEmpty,
    ScreenDescriptionIsEmpty,
    UnknownSourceType,
)
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from telegram import CallbackQuery, Update
    from telegram._files.photosize import PhotoSize
    from telegram._utils.types import FileInput
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

    from hammett.core.hiders import Hider, HidersChecker
    from hammett.types import Handler, Keyboard, Source, Stage

EMPTY_KEYBOARD: 'Keyboard' = []

LOGGER = logging.getLogger(__name__)


class Button:
    """The class implements the interface of a button."""

    hiders_checker: 'HidersChecker | None' = None

    def __init__(
        self: 'Self',
        caption: str,
        source: 'Source',
        *,
        source_type: SourcesTypes = SourcesTypes.HANDLER_SOURCE_TYPE,
        hiders: 'Hider | None' = None,
        payload: str | None = None,
    ) -> None:
        self.caption = caption
        self.payload = payload
        self.source = source
        self.source_wrapped = None
        self.source_type = source_type
        self.hiders = hiders

        self._check_source()
        self._init_hider_checker()

    #
    # Private methods
    #

    def _check_source(self: 'Self') -> None:
        """Checks if the source is valid. If it's invalid, the method raises `TypeError`."""

        if self.source_type == SourcesTypes.GOTO_SOURCE_TYPE:
            screen = cast('type[Screen]', self.source)
            if issubclass(screen, Screen):
                self.source_goto = cast('Handler[..., Stage]', screen().goto)
            else:
                msg = (
                    f'The source "{self.source}" must be a subclass of Screen if its '
                    f'source_type is SourcesTypes.GOTO_SOURCE_TYPE'
                )
                raise TypeError(msg)

        if self.source_type == SourcesTypes.HANDLER_SOURCE_TYPE and not callable(self.source):
            msg = (
                f'The source "{self.source}" must be callable if its '
                f'source_type is SourcesTypes.HANDLER_SOURCE_TYPE'
            )
            raise TypeError(msg)

    def _init_hider_checker(self: 'Self') -> None:
        if self.hiders and not self.hiders_checker:
            from hammett.conf import settings

            if not settings.HIDERS_CHECKER:
                msg = "The 'HIDERS_CHECKER' setting is not set"
                raise ImproperlyConfigured(msg)

            if self.hiders:
                hiders_checker: type['HidersChecker'] = import_string(settings.HIDERS_CHECKER)
                self.hiders_checker = hiders_checker(self.hiders.hiders_set)

    async def _specify_visibility(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        visibility = True
        if (
            self.hiders and
            self.hiders_checker and
            not await self.hiders_checker.run(update, context)
        ):
            visibility = False

        return visibility

    #
    # Public methods
    #

    async def create(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> tuple[InlineKeyboardButton, bool]:
        """Creates the button."""

        visibility = await self._specify_visibility(update, context)

        if self.source_type in (SourcesTypes.GOTO_SOURCE_TYPE, SourcesTypes.HANDLER_SOURCE_TYPE):
            if self.source_type == SourcesTypes.GOTO_SOURCE_TYPE and self.source_goto:
                source = self.source_goto
            else:
                source = cast('Handler[..., Stage]', self.source)

            data = (
                f'{handlers.calc_checksum(source)},'
                f'button={handlers.calc_checksum(self.caption)},'
                f'user_id={update.effective_user.id}'  # type: ignore[union-attr]
            )

            if self.payload is not None:
                payload_storage = handlers.get_payload_storage(context)
                payload_storage[data] = self.payload

            return InlineKeyboardButton(self.caption, callback_data=data), visibility

        if self.source_type == SourcesTypes.URL_SOURCE_TYPE and isinstance(self.source, str):
            return InlineKeyboardButton(self.caption, url=self.source), visibility

        raise UnknownSourceType


@dataclass
class RenderConfig:
    """The class that represents a config for the Screen render method."""

    as_new_message: bool = False
    cache_covers: bool = False
    cover: 'str | PathLike[str]' = ''
    description: str = ''
    keyboard: 'Keyboard | None' = None


class Screen:
    """The class implements the interface of a screen."""

    cache_covers: bool = False
    cover: 'str | PathLike[str]' = ''
    description: str = ''
    html_parse_mode: 'ParseMode | DefaultValue[None]' = DEFAULT_NONE

    _cached_covers: dict[str | PathLike[str], str] = {}
    _initialized: bool = False
    _instance: 'Screen | None' = None

    def __init__(self: 'Self') -> None:
        if not self._initialized:
            if self.html_parse_mode is DEFAULT_NONE:
                from hammett.conf import settings
                self.html_parse_mode = settings.HTML_PARSE_MODE

            self._initialized = True

    def __new__(cls: type['Screen'], *args: 'Any', **kwargs: 'Any') -> 'Screen':
        """Implements the singleton pattern."""

        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)

        return cls._instance

    #
    # Private methods
    #

    def _create_input_media_photo(
        self: 'Self',
        caption: str,
        media: 'FileInput | PhotoSize',
    ) -> InputMediaPhoto:
        """Creates an object that represents a photo to be sent."""

        return InputMediaPhoto(
            caption=caption,
            media=media,
            parse_mode=ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE,
        )

    @staticmethod
    async def _create_markup_keyboard(
        rows: 'Keyboard',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> InlineKeyboardMarkup:
        keyboard = []
        for row in rows:
            buttons = []
            for button in row:
                inline_button, visible = await button.create(update, context)
                if visible:
                    buttons.append(inline_button)

            keyboard.append(buttons)

        return InlineKeyboardMarkup(keyboard)

    async def _get_edit_render_method(
        self: 'Self',
        update: 'Update',
        *,
        cache_covers: bool = False,
        cover: 'str | PathLike[str]' = '',
        description: str = '',
    ) -> tuple['Callable[..., Awaitable[Any]] | None', dict[str, 'Any']]:
        """Returns the render method and its kwargs for editing a message."""

        kwargs: 'Any' = {}
        send: 'Callable[..., Awaitable[Any]] | None' = None

        query = await self.get_callback_query(update)
        if query:
            if cover:
                if self._is_url(cover):
                    kwargs['media'] = self._create_input_media_photo(
                        caption=description,
                        media=str(cover) if cache_covers else f'{cover}?{uuid4()}',
                    )
                elif cover in self._cached_covers:
                    kwargs['media'] = self._create_input_media_photo(
                        caption=description,
                        media=self._cached_covers[cover],
                    )
                else:
                    with Path(cover).open('rb') as infile:
                        kwargs['media'] = self._create_input_media_photo(
                            caption=description,
                            media=infile,
                        )

                send = query.edit_message_media
            else:
                kwargs['parse_mode'] = ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE
                kwargs['text'] = description
                send = query.edit_message_text

        return send, kwargs

    async def _get_new_message_render_method(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        cache_covers: bool = False,
        cover: 'str | PathLike[str]' = '',
        description: str = '',
    ) -> tuple['Callable[..., Awaitable[Any]]', dict[str, 'Any']]:
        """Returns the render method and its kwargs for sending a new message."""

        kwargs: 'Any' = {
            'parse_mode': ParseMode.HTML if self.html_parse_mode else DEFAULT_NONE,
        }

        if update.effective_chat:
            chat_id = update.effective_chat.id
            kwargs['chat_id'] = chat_id

        if cover:
            if self._is_url(cover) and cache_covers:
                cover = f'{cover}?{uuid4()}'
            elif cache_covers:
                cover_file_id = self._cached_covers.get(cover)
                cover = cover_file_id if cover_file_id else cover

            kwargs['caption'] = description
            kwargs['photo'] = cover

            send = context.bot.send_photo
        else:
            kwargs['text'] = description

            send = context.bot.send_message

        return send, kwargs

    @staticmethod
    def _is_url(cover: 'str | PathLike[str]') -> bool:
        """Checks if the cover is specified using either a local path or a URL."""

        return bool(re.search(r'^https?://', str(cover)))

    #
    # Public methods
    #

    @staticmethod
    async def get_callback_query(update: 'Update') -> 'CallbackQuery | None':
        """Gets CallbackQuery from Update."""

        query = update.callback_query
        # CallbackQueries need to be answered, even if no notification to the user is needed.
        # Some clients may have trouble otherwise.
        # See https://core.telegram.org/bots/api#callbackquery
        if query:
            await query.answer()

        return query

    async def get_payload(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> str:
        """Returns the payload passed through the pressed button."""

        query = await self.get_callback_query(update)
        data = getattr(query, 'data', None)
        if data is None:
            raise FailedToGetDataAttributeOfQuery

        try:
            payload_storage = handlers.get_payload_storage(context)
            return payload_storage.pop(data)
        except KeyError as exc:
            raise PayloadIsEmpty from exc

    async def goto(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Switches to the screen."""

        await self.render(update, context)
        return DEFAULT_STAGE

    async def render(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
        *,
        config: 'RenderConfig | None' = None,
    ) -> None:
        """Renders the screen components (i.e., cover, description and keyboard)."""

        config = config or RenderConfig()
        cache_covers = config.cache_covers or self.cache_covers
        cover = config.cover or self.cover
        description = config.description or self.description
        if not description:
            msg = f'The description of {self.__class__.__name__} is empty'
            raise ScreenDescriptionIsEmpty(msg)

        if config.keyboard is None:
            config.keyboard = config.keyboard or self.setup_keyboard()

        send: 'Callable[..., Awaitable[Any]] | None' = None
        if config.as_new_message:
            send, kwargs = await self._get_new_message_render_method(
                update,
                context,
                cache_covers=cache_covers,
                cover=cover,
                description=description,
            )
        else:
            send, kwargs = await self._get_edit_render_method(
                update,
                cache_covers=cache_covers,
                cover=cover,
                description=description,
            )

        if send:
            send_object = await send(
                reply_markup=await self._create_markup_keyboard(config.keyboard, update, context),
                **kwargs,
            )
            if cover and cache_covers and not self._is_url(cover):
                photo_size_object = send_object.photo[-1]
                self._cached_covers[cover] = photo_size_object.file_id

    def setup_keyboard(self: 'Self') -> 'Keyboard':
        """Sets up the keyboard for the screen."""

        return EMPTY_KEYBOARD


class StartScreen(Screen):
    """The base class for the start screens (i.e, the screens
    that show up on the /start command).
    """

    async def start(
        self: 'Self',
        update: 'Update',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> 'Stage':
        """Invoked on the /start command."""

        raise NotImplementedError
