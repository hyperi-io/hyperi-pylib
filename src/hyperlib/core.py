"""
Core functionality for {{ package_name }}.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from loguru import logger
from dynaconf import Dynaconf

# Version (managed by semantic-release)
__version__ = "0.1.0"

# Load configuration
settings = Dynaconf(
    envvar_prefix="{{ package_name | upper }}",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True,
)

# Configure logger using hyperlib config cascade (CLI → ENV → .env → config → default → hardcoded)
from hyperlib.config import get_logging_config as _get_logging_config
try:
    _logging_config = _get_logging_config()
    log_level = _logging_config.get("level", "INFO")
except:
    # Fallback if config not available during initialization
    log_level = settings.get("logging", {}).get("level", "INFO")

# Remove default logger and add configured one
logger.remove()
logger.add(
    sys.stderr,
    level=log_level.upper(),
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Initialize logger
logger.info(f"Initializing {{ package_name }} v{__version__}")