"""The module contains the settings of the demo."""

import contextlib
import os

with contextlib.suppress(ImportError):
    from dotenv import load_dotenv
    load_dotenv()

ADMIN_GROUP = []

HIDERS_CHECKER = 'hiders_checker.DemoHidersChecker'

REDIS_PERSISTENCE = {
    'HOST': 'valkey',
    'PORT': 6379,
    'DB': os.getenv('REDIS_PERSISTENCE_DB', '1'),
}

TOKEN = os.getenv('TOKEN', '')
