"""
HyperLib - Enterprise Infrastructure for Containerized Python Applications
Provides configuration, logging, timeout, and container management

Requires Python 3.11+ for modern type hints and enterprise features
"""

__version__ = "1.1.1"

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
from . import bootstrap

# Re-export commonly used functions for convenience
from .logger import get_logger, setup as setup_logger
from .config import get_logging_config
from .bootstrap import load_dotenv, list_sorted_scripts, load_defaults_yaml, ensure_dependency

__all__ = [
    'config', 'logger', 'timeout', 'container', 'bootstrap',
    'get_logger', 'setup_logger', 'get_logging_config',
    'load_dotenv', 'list_sorted_scripts', 'load_defaults_yaml', 'ensure_dependency',
    '__version__'
]