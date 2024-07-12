"""The module contains functions for working with dynamic descriptions."""


def render(template: str, context: dict[str, str]) -> str:
    """Return a description after formatting it using passed tags."""
    description = template
    for key, val in context.items():
        description = description.replace(f'{{{key}}}', str(val))

    return description
