"""The module contains methods for working with templates."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any


class Template:
    """The class implements methods for working with the template file."""

    def __init__(self, path: 'Path') -> None:
        """Save the path to the template file."""
        self.path = path
        self.file: bytes | None = None

    def load(self) -> 'Template':
        """Load the template file."""
        with self.path.open('rb') as file:
            self.file = file.read()

        return self

    def render(self, **kwargs: 'Any') -> bytes:
        """Put the variables into the template."""
        if not self.file:
            msg = 'Template is not loaded'
            raise FileNotFoundError(msg)

        for key, value in kwargs.items():
            raw_value = value.encode()
            self.file = self.file.replace(
                f'{{{{{key}}}}}'.encode(), raw_value,
            ).replace(
                f'{{{{ {key} }}}}'.encode(),
                raw_value,
            )

        return self.file
