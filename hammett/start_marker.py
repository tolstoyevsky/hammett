"""The module contains a start-markers parser."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self


class StartMarker:
    """The class implements a start-markers parser."""

    def __init__(self: 'Self', start_marker: str) -> None:
        """Initialize a start-markers parser object."""
        self._start_marker = start_marker
        self._result: dict[str, str] = {}

        self._parse()

    def __getitem__(self: 'Self', item: str) -> str:
        """Return an element by a key."""
        return self._result[item]

    def _parse(self: 'Self') -> None:
        """Parse start-makers."""
        markers = self._start_marker[len('/start '):]
        if markers:
            markers = markers[1:] if markers.startswith('=') else markers
            markers = markers[:-1] if markers.endswith('=') else markers

            parts = markers.split('=')
            if len(parts) % 2 != 0:
                parts = ['source', *parts]

            keys = parts[::2]
            values = parts[1::2]
            self._result = dict(zip(keys, values, strict=False))
