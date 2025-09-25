"""
Core functionality for {{ package_name }}.
"""

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

# Initialize logger
logger.info(f"Initializing {{ package_name }} v{__version__}")