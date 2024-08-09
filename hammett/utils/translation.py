"""The module contains tools for localization."""

import gettext as native_gettext

from hammett.conf import settings
from hammett.core.exceptions import LocalePathIsNotSpecified


def gettext(caption: str, language: str = settings.LANGUAGE_CODE) -> str:
    """Return translated text by its caption.

    Returns
    -------
        Translated text by its caption.

    Raises
    ------
        LocalePathIsNotSpecified: If the `LOCALE_PATH` attribute of settings is not specified.

    """
    if not settings.LOCALE_PATH:
        raise LocalePathIsNotSpecified

    translation = native_gettext.translation(
        settings.DOMAIN,
        localedir=str(settings.LOCALE_PATH),
        languages=[language],
        fallback=True,
    )
    translation.install()

    return translation.gettext(caption)
