"""The package contains functions to collect handler statistics and further represent them."""

__all__ = (
    'StopWatchEventLoopPolicy',
    'StopWatchSelector',
    'collect_handler_statistics',
)

from hammett.stopwatch.collector import collect_handler_statistics
from hammett.stopwatch.event_loop import StopWatchEventLoopPolicy, StopWatchSelector
