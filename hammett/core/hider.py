"""The module contains the implementation of the hider mechanism."""

import asyncio
from typing import TYPE_CHECKING

from hammett.core.exceptions import HiderIsUnregistered

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from typing import Any

    from telegram import Update
    from telegram.ext import CallbackContext
    from telegram.ext._utils.types import BD, BT, CD, UD
    from typing_extensions import Self

(
    ONLY_FOR_ADMIN,
    ONLY_FOR_BETA_TESTERS,
    ONLY_FOR_MODERATORS,
) = range(3)


class Hider:
    """The class implements a hider."""

    def __init__(self: 'Self', hider: int) -> None:
        """Initialize a hider object."""
        self.hider: int = hider
        self.hiders_set: set[int] = {hider}

    def __eq__(self, other: object) -> bool:
        """Compare two Hider objects.

        Returns
        -------
            Result of comparing two Hider objects.

        """
        if not isinstance(other, Hider):
            return super().__eq__(other)

        return self.hider == other.hider and self.hiders_set == other.hiders_set

    def __hash__(self) -> int:
        """Return object hash.

        Returns
        -------
            Object hash.

        """
        return hash((self.hider, self.hiders_set))

    def __or__(self: 'Self', other: 'Hider') -> 'Self':
        """Perform `or` operation.

        Returns
        -------
            Instance of the hider.

        """
        self.hiders_set.add(other.hider)
        return self


class HidersChecker:
    """The base class for the implementations of custom hiders checkers."""

    def __init__(self: 'Self', hiders_set: set[int]) -> None:
        """Initialize a hider checker object."""
        if getattr(self, 'custom_hiders', None) is None:
            self.custom_hiders: dict[int, Callable[[Any, Any], Awaitable[Any]]] = {}

        self._hiders_set = hiders_set
        self._registered_hiders: dict[int, Callable[[Any, Any], Awaitable[Any]]] = {}
        self._register_hiders()

    #
    # Private methods
    #

    def _register_hiders(self: 'Self') -> None:
        self._registered_hiders = {
            ONLY_FOR_ADMIN: self.is_admin,
            ONLY_FOR_BETA_TESTERS: self.is_beta_tester,
            ONLY_FOR_MODERATORS: self.is_moderator,
            **self.custom_hiders,
        }

    #
    # Public methods
    #

    async def is_admin(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Represent a stub for checking whether the user is an admin.

        Returns
        -------
            Result of checking whether the user is an admin.

        """
        return False

    async def is_beta_tester(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Represent a stub for checking whether the user is a beta tester.

        Returns
        -------
            Result of checking whether the user is a beta tester.

        """
        return False

    async def is_moderator(
        self: 'Self',
        _update: 'Update',
        _context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Represent a stub for checking whether the user is a moderator.

        Returns
        -------
            Result of checking whether the user is a moderator.

        """
        return False

    async def run(
        self: 'Self',
        update: 'Update | None',
        context: 'CallbackContext[BT, UD, CD, BD]',
    ) -> bool:
        """Run the checks associated with the registered hiders.
        The hiders are combined into chains using the OR operator, so the method
        returns True if any of the checks is True.
        The method is invoked under the hood, so you should not run it directly.

        Returns
        -------
            True if any of the HiderChecker checks are True.

        """
        for hider in self._hiders_set:
            try:
                hider_handler = self._registered_hiders[hider]
            except KeyError as exc:
                msg = f"The hider '{hider}' is unregistered"
                raise HiderIsUnregistered(msg) from exc

            if asyncio.iscoroutinefunction(hider_handler):
                if await hider_handler(update, context):
                    return True
            elif hider_handler(update, context):
                return True

        return False
