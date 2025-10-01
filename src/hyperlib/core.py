"""
Core functionality for {{ package_name }}.
"""

import sys

from dynaconf import Dynaconf
from loguru import logger

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
except:
    # Fallback if config not available during initialization
    _logging_config = {
        "level": "INFO",
        "format": "console",
        "output": "stderr",
        "color": True,
        "timestamp_format": "rfc3339",
        "caller": True,
        "stacktrace_level": "ERROR",
    }


# Build format string based on configuration
def _build_log_format(config: dict) -> str:
    """Build loguru format string from configuration."""
    log_format = config.get("format", "console")
    use_color = config.get("color", True)
    include_caller = config.get("caller", True)
    timestamp_fmt = config.get("timestamp_format", "rfc3339")

    # Timestamp format mapping
    timestamp_formats = {
        "rfc3339": "YYYY-MM-DDTHH:mm:ss.SSSZ",
        "iso8601": "YYYY-MM-DD HH:mm:ss.SSS",
        "unix": "X",
        "epoch": "x",
    }
    time_format = timestamp_formats.get(timestamp_fmt, "YYYY-MM-DDTHH:mm:ss.SSSZ")

    if log_format == "json":
        # JSON format for production/K8s
        return (
            '{{"timestamp":"{time:'
            + time_format
            + '}", "level":"{level}", "name":"{name}", "function":"{function}", "line":{line}, "message":"{message}"}}\n'
        )
    elif log_format == "logfmt":
        # logfmt format (key=value pairs)
        if include_caller:
            return (
                "time={time:"
                + time_format
                + '} level={level} name={name} function={function} line={line} msg="{message}"\n'
            )
        else:
            return "time={time:" + time_format + '} level={level} msg="{message}"\n'
    elif log_format == "text":
        # Simple text format (no colors)
        if include_caller:
            return "{time:" + time_format + "} | {level: <8} | {name}:{function}:{line} - {message}\n"
        else:
            return "{time:" + time_format + "} | {level: <8} | {message}\n"
    else:  # console (default)
        # Console format with optional colors
        if use_color:
            if include_caller:
                return (
                    "<green>{time:"
                    + time_format
                    + "}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>\n"
                )
            else:
                return (
                    "<green>{time:"
                    + time_format
                    + "}</green> | <level>{level: <8}</level> | <level>{message}</level>\n"
                )
        else:
            if include_caller:
                return "{time:" + time_format + "} | {level: <8} | {name}:{function}:{line} - {message}\n"
            else:
                return "{time:" + time_format + "} | {level: <8} | {message}\n"


# Determine output destination
output_dest = _logging_config.get("output", "stderr")
if output_dest == "stdout":
    sink = sys.stdout
elif output_dest == "file":
    sink = _logging_config.get("file", sys.stderr)
else:  # stderr (default)
    sink = sys.stderr

# Configure logger
logger.remove()
logger.add(
    sink,
    level=_logging_config.get("level", "INFO").upper(),
    format=_build_log_format(_logging_config),
    colorize=_logging_config.get("color", True) and _logging_config.get("format", "console") in ("console",),
    backtrace=True,
    diagnose=True,
)

# Initialize logger
logger.info(f"Initializing {{ package_name }} v{__version__}")
