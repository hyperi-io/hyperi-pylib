"""
HyperLib - Enterprise Infrastructure for Containerized Python Applications
Provides configuration, logging, timeout, and container management

Requires Python 3.11+ for modern type hints and enterprise features
"""

__version__ = "1.2.0"

# Enforce Python 3.11+ requirement
import sys

from . import bootstrap, config, container, logger, timeout
from .bootstrap import ensure_dependency, list_sorted_scripts, load_defaults_yaml, load_dotenv
from .config import get_logging_config

# Re-export commonly used functions for convenience
from .logger import get_logger
from .logger import setup as setup_logger

__all__ = [
    "config",
    "logger",
    "timeout",
    "container",
    "bootstrap",
    "get_logger",
    "setup_logger",
    "get_logging_config",
    "load_dotenv",
    "list_sorted_scripts",
    "load_defaults_yaml",
    "ensure_dependency",
    "__version__",
]
