"""
HyperLib - Enterprise Infrastructure for Containerized Python Applications
Provides configuration, logging, timeout, and container management

Requires Python 3.11+ for modern type hints and enterprise features
"""

__version__ = "0.1.0"

# Enforce Python 3.11+ requirement
import sys
if sys.version_info < (3, 11):
    raise RuntimeError(
        f"HyperLib requires Python 3.11 or newer. "
        f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
    )

from . import config
from . import logger
from . import timeout
from . import container

__all__ = ['config', 'logger', 'timeout', 'container', '__version__']