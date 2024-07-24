"""The module contains the settings of the demo."""

import os

ADMIN_GROUP = []

HIDERS_CHECKER = 'demos.hiders.hiders_checker.DemoHidersChecker'

TOKEN = os.getenv('TOKEN', '')
