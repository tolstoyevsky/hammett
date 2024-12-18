"""The module contains tools for working with handlers."""

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hammett.types import HANDLER_ASSIGNMENTS_TYPE, Func

HANDLER_ASSIGNMENTS = (*functools.WRAPPER_ASSIGNMENTS, '__self__')


def wraps_handler(
    wrapped: 'Func',
    assigned: 'HANDLER_ASSIGNMENTS_TYPE' = HANDLER_ASSIGNMENTS,
    updated: tuple[str] = functools.WRAPPER_UPDATES,
) -> 'functools.partial[Func]':
    """Identical to `functools.wraps`, the only thing different is the `assigned` argument.
    This is required for `calc_checksum` function to return a valid result even
    for a decorated handler. Should be used if a decorator for the handler is implemented.

    Returns
    -------
        New function with partial application of the given arguments and keywords.

    """
    return functools.partial(
        functools.update_wrapper,
        wrapped=wrapped,
        assigned=assigned,
        updated=updated,
    )
