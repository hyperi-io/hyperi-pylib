"""
HyperLib Bootstrap Utilities - Helpers for bootstrap and CI scripts
These utilities support the bootstrap process and are not part of the main API.
"""

import os
import subprocess
import yaml
from pathlib import Path
from typing import List, Tuple, Any, Dict


def load_dotenv() -> None:
    """Load environment variables from .env file if present.

    Searches for .env starting from current directory, walking up to find project root.
    Does NOT override existing environment variables.
    Supports basic variable expansion: ${VAR_NAME}
    """
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        env_file = parent / ".env"
        if env_file.exists():
            _load_env_file(env_file)
            break


def _load_env_file(env_file: Path) -> None:
    """Load a single .env file."""
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                # Simple variable expansion for ${VAR}
                if "${" in value:
                    import re
                    for match in re.findall(r'\$\{([^}]+)\}', value):
                        value = value.replace(f"${{{match}}}", os.environ.get(match, ""))
                os.environ.setdefault(key, value)


def list_sorted_scripts(directory: Path, patterns: Tuple[str, ...] = (".sh", ".py")) -> List[Path]:
    """List scripts in directory matching patterns, sorted by name.

    Args:
        directory: Directory to search
        patterns: File extensions to match (default: .sh and .py)

    Returns:
        List of Path objects sorted by filename
    """
    if not directory.exists():
        return []

    scripts = []
    for pattern in patterns:
        scripts.extend(directory.glob(f"*{pattern}"))

    return sorted(scripts, key=lambda p: p.name)


def load_defaults_yaml() -> Dict[str, Any]:
    """Load defaults from scripts/ci.yaml or scripts/ci.yml.

    Returns:
        Dictionary of configuration values, empty dict if file not found
    """
    for filename in ["ci.yaml", "ci.yml"]:
        ci_file = Path.cwd() / "scripts" / filename
        if ci_file.exists():
            with open(ci_file) as f:
                return yaml.safe_load(f) or {}

    return {}


def ensure_dependency(command: str, install: bool, logger, defaults: Dict[str, Any]) -> None:
    """Ensure a command is available, optionally installing it.

    Args:
        command: Command to check for (e.g., "semantic-release")
        install: Whether to install if missing
        logger: Logger instance for output
        defaults: Configuration dict from ci.yaml

    Raises:
        SystemExit: If command is missing and install=False
    """
    # Check if command exists
    if subprocess.run(["which", command], capture_output=True).returncode == 0:
        logger.info(f"{command} found")
        return

    if not install:
        logger.error(f"{command} not found (install with --install)")
        raise SystemExit(1)

    # Try to install from defaults config
    install_cmds = defaults.get("dependencies", {}).get(command, {}).get("install", [])
    if not install_cmds:
        logger.error(f"No install command configured for {command}")
        raise SystemExit(1)

    logger.info(f"Installing {command}...")
    for cmd in install_cmds:
        try:
            subprocess.check_call(cmd, shell=True)
            logger.info(f"{command} installed successfully")
            return
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {command}: {e}")
            raise SystemExit(1)


__all__ = [
    'load_dotenv',
    'list_sorted_scripts',
    'load_defaults_yaml',
    'ensure_dependency',
]