"""The module contains the settings of the demo."""

import os
from pathlib import Path

MEDIA_ROOT = Path(__file__).resolve().parent / 'media'

TOKEN = os.getenv('TOKEN', '')
