"""The module contains a decorator that wraps handlers to track time."""

import asyncio
import functools
import logging
import time
from typing import TYPE_CHECKING

from hammett.conf import settings
from hammett.core.exceptions import ImproperlyConfigured
from hammett.stopwatch.event_loop import StopWatchSelector
from hammett.utils.handler import wraps_handler
from hammett.utils.module_loading import import_string

if TYPE_CHECKING:
    from typing import Any

    from hammett.core.constants import HandlerStats
    from hammett.stopwatch.stats import BaseStatsProcessor
    from hammett.types import Handler

LOGGER = logging.getLogger(__name__)


@functools.cache
def get_stopwatch_stats_processor() -> 'type[BaseStatsProcessor]':
    """Import a stopwatch stats processor by the `STOPWATCH_STATS_PROCESSOR` of the module path
    and returns it.
    """
    try:
        processor = import_string(settings.STOPWATCH_STATS_PROCESSOR)
    except ImportError as exc:
        msg = (
            f'The module could not be imported: {settings.STOPWATCH_STATS_PROCESSOR}. '
            f'Check your STOPWATCH_STATS_PROCESSOR setting.'
        )
        raise ImproperlyConfigured(msg) from exc
    else:
        return processor


def collect_handler_statistics(func: 'Handler') -> 'Handler':
    """Collect the statistics of the handler and passes them to the `STOPWATCH_STATS`."""
    stats_processor = get_stopwatch_stats_processor()

    @wraps_handler(func)
    async def wrapper(*args: 'Any', **kwargs: 'Any') -> 'Any':
        try:
            event_loop_selector = getattr(asyncio.get_event_loop(), '_selector')  # noqa: B009
        except AttributeError:
            event_loop_selector = None

        if event_loop_selector is None or not isinstance(event_loop_selector, StopWatchSelector):
            is_possible_get_select_time = False
            LOGGER.error(
                'Unable to get select time statistic. Perhaps you have changed the '
                'event loop policy?',
            )
        else:
            is_possible_get_select_time = True
            event_loop_selector.reset_select_time()

        real_time = time.time()
        process_time = time.process_time()

        response = await func(*args, **kwargs)

        real_time = time.time() - real_time
        cpu_time = time.process_time() - process_time

        select_time = event_loop_selector.select_time if is_possible_get_select_time else 0.0
        other_io_time = max(0.0, real_time - cpu_time - select_time)

        stats: HandlerStats = {
            'cpu_time': cpu_time,
            'select_time': select_time,
            'other_io_time': other_io_time,
            'real_time': real_time,
        }
        await stats_processor(func, stats).process()

        return response

    return wrapper
