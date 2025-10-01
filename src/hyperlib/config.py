"""
HyperLib Config - Standard Dynaconf Interface
Enforces consistent configuration usage across ALL /src code
"""

from pathlib import Path
from dynaconf import Dynaconf

# Initialize container-aware dynaconf configuration
current_file = Path(__file__)
if "/src/hyperlib/" in str(current_file):
    # Development: use container simulation
    project_root = current_file.parent.parent.parent
    container_root = project_root / "container"
else:
    # Production: use actual container paths
    container_root = Path("/")

config_dir = container_root / "app" / "config"

settings = Dynaconf(
    envvar_prefix="APP",  # Environment variables use APP_ prefix
    settings_files=[
        str(config_dir / "config.yaml"),           # Override config (4th priority)
        str(config_dir / "dfe_ai" / "default.yaml")  # Default config (5th priority)
    ],
    load_dotenv=True,  # Load .env file (3rd priority)
    environments=False,  # Single config approach
    # PRECEDENCE: CLI → ENV → .env → config override → default → hardcoded
)

def get_settings():
    """Get standard dynaconf settings object"""
    return settings

def setup():
    """Setup configuration (for compatibility)"""
    return settings

# Standard configuration access functions
def get_api_config():
    """Get API configuration"""
    api_config = settings.get("api", {})
    return {
        "max_retries": api_config.get("max_retries", 3),
        "retry_delay": api_config.get("retry_delay", 5),
        "timeout": api_config.get("timeout", 120)
    }

def get_logging_config():
    """Get container-aware logging configuration with LOG_LEVEL support.

    Priority order (CLI → ENV → .env → config → default → hardcoded):
    1. LOG_LEVEL environment variable (standard)
    2. APP_LOGGING__LEVEL (Dynaconf prefixed)
    3. Config file logging.level
    4. Hardcoded default (INFO)
    """
    import os

    logging_config = settings.get("logging", {})

    # Check for LOG_LEVEL environment variable first (standard convention)
    log_level = os.getenv("LOG_LEVEL")
    if not log_level:
        # Fall back to dynaconf settings
        log_level = logging_config.get("level", "INFO")

    # Get container-aware log file path
    log_file = logging_config.get("file")
    if log_file and not log_file.startswith("/"):
        # Relative path - make it container-aware
        log_file = str(container_root / "var" / "log" / "dfe_ai" / log_file)

    return {
        "level": log_level,
        "console": logging_config.get("console", True),
        "file": log_file
    }

# Export for direct access
__all__ = ['settings', 'get_settings', 'setup', 'get_api_config', 'get_logging_config']