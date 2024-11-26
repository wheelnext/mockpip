#!/usr/bin/env python

import importlib.metadata

__version__ = importlib.metadata.version("mockpip")

# Initialize the logger
from mockpip import logger  # noqa: F401
