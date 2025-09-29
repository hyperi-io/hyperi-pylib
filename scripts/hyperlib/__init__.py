#!/usr/bin/env python3
from __future__ import annotations

"""
hyperlib: shared helpers for core CI/bootstrap scripts.

This module is intended to be a small, importable library shipped inside
the core subtree (`subtrees/hypersec-forge-core/scripts/hyperlib`).

Responsibilities:
- load defaults from `scripts/ci.yaml` and populate environment fallbacks
- provide a standardized Solarized logger + optional file/JSON output
- ensure a reproducible `.venv-ci` for CI tooling and re-exec into it
- helpers to list and run `.d` style scripts in sorted order

The goal is to keep all bootstrap/CI entrypoints (Python or shell) using the
same logging, configuration, and venv creation/re-exec behavior so child
templates can assume a consistent runtime (tools available in `.venv-ci/bin`).
"""

import json
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Tuple

PROTOCOL_NOTE = (
    "Entrypoints (scripts/ci, scripts/bootstrap) use hyperlib.ensure_ci_venv_and_reexec() "
    "to create .venv-ci (if missing) and re-exec under that venv. After re-exec, "
    "all subsequent checks/install actions are executed using the .venv-ci Python and tools."
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# -------------------------- Defaults loading -------------------------------

def load_defaults_yaml() -> dict:
    # Renamed defaults -> ci.yaml to include CI-specific dependency mappings
    cfg_path = PROJECT_ROOT / "scripts" / "ci.yaml"
    data: dict = {}
    if not cfg_path.exists():
        return data
    try:
        import yaml  # type: ignore
    except Exception:
        # Minimal YAML loader fallback for key: value pairs
        for line in cfg_path.read_text(encoding="utf-8").splitlines():
            ln = line.strip()
            if not ln or ln.startswith("#") or ":" not in ln:
                continue
            k, v = ln.split(":", 1)
            data[k.strip()] = v.strip().strip('"')
        return data
    with cfg_path.open("r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f) or {}
    return loaded


def apply_defaults_env(defaults: dict) -> None:
    if not isinstance(defaults, dict):
        return
    ci = defaults.get("ci", {})
    if not isinstance(ci, dict):
        return
    for env_key, cfg_key in (
        ("HSF_CI_VENV", "venv_name"),
        ("HSF_PREFERRED_PYTHON", "preferred_python"),
        ("HSF_MIN_PYTHON", "min_python"),
    ):
        val = ci.get(cfg_key)
        if isinstance(val, str) and val and env_key not in os.environ:
            os.environ[env_key] = val


# -------------------------- Logging ----------------------------------------

def _is_tty() -> bool:
    try:
        return sys.stdout.isatty() and not os.environ.get("NO_COLOR")
    except Exception:
        return False


class SolarizedFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[38;5;33m",
        "INFO": "\033[38;5;64m",
        "OK": "\033[38;5;64m",
        "WARNING": "\033[38;5;136m",
        "ERROR": "\033[38;5;160m",
        "CRITICAL": "\033[38;5;160m",
    }
    CYAN = "\033[36m"
    TIME = "\033[38;5;64m"
    RESET = "\033[0m"

    def formatTime(self, record, datefmt=None):
        dt = datetime.now().astimezone()
        if datefmt and "%f" in datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")[:-3]

    def format(self, record: logging.LogRecord) -> str:
        t = self.formatTime(record)
        level = record.levelname
        name = record.name
        func = record.funcName
        line = record.lineno
        msg = record.getMessage()
        if _is_tty():
            lvl_color = self.COLORS.get(level, self.CYAN)
            return (
                f"{self.TIME}{t}{self.RESET} | "
                f"{lvl_color}{level:<8}{self.RESET} | "
                f"{self.CYAN}{name}{self.RESET}:{self.CYAN}{func}{self.RESET}:{self.CYAN}{line}{self.RESET} - "
                f"{lvl_color}{msg}{self.RESET}"
            )
        return f"{t} | {level:<8} | {name}:{func}:{line} - {msg}"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(SolarizedFormatter())
    logger.addHandler(sh)

    log_file = os.environ.get("CI_LOG_FILE")
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        if os.environ.get("CI_LOG_STRUCTURED") == "1":
            class JSONFormatter(logging.Formatter):
                def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
                    t = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S.%f%z")[:-3]
                    payload = {
                        "time": t,
                        "level": record.levelname,
                        "name": record.name,
                        "function": record.funcName,
                        "line": record.lineno,
                        "message": record.getMessage(),
                    }
                    return json.dumps(payload, ensure_ascii=True)

            fh = logging.FileHandler(log_file)
            fh.setFormatter(JSONFormatter())
            logger.addHandler(fh)
        else:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(
                logging.Formatter(
                    fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
                    datefmt="%Y-%m-%dT%H:%M:%S.%f%z",
                )
            )
            logger.addHandler(fh)
    return logger


# -------------------------- Venv handling ----------------------------------

@dataclass
class VenvConfig:
    path: Path
    preferred_python: str
    min_python: str


def running_in_ci_venv(cfg: VenvConfig) -> bool:
    """Return True when the current process is already running inside the
    `.venv-ci` environment created by the bootstrap.

    We rely on either the marker env `HSF_IN_CI_VENV=1` (set by re-exec) or
    a sys.prefix that ends with the venv folder name. Child scripts should
    NOT attempt to recreate the venv; the core bootstrap is responsible for
    creating and re-execing into it.
    """
    return os.environ.get("HSF_IN_CI_VENV") == "1" or str(sys.prefix).endswith("/" + cfg.path.name)


def _python_matches_version(py: str, major_minor: str) -> bool:
    try:
        out = subprocess.check_output([py, "-c", "import sys;print(f'{sys.version_info[0]}.{sys.version_info[1]}')"], text=True).strip()
        return out == major_minor
    except Exception:
        return False


def _resolve_python(preferred: str) -> str | None:
    candidates = [f"python{preferred}", "python3", sys.executable]
    for cand in candidates:
        p = shutil.which(cand)
        if not p:
            continue
        if _python_matches_version(p, preferred):
            return p
    return None


def create_ci_venv(cfg: VenvConfig, logger: logging.Logger) -> None:
    """Create .venv-ci for CI tooling. Never touches OS Python."""
    if shutil.which("uv"):
        logger.info("Creating %s with uv (python=%s)", cfg.path, cfg.preferred_python)
        try:
            # Create venv with uv
            subprocess.check_call(["uv", "venv", str(cfg.path), "--python", cfg.preferred_python])
        except Exception:
            subprocess.check_call(["uv", "venv", str(cfg.path)])
        
        # Install minimal deps using uv (safer than venv pip)
        logger.info("Installing base dependencies with uv")
        subprocess.check_call([
            "uv", "pip", "install", 
            "--python", str(cfg.path),
            "-q", "--upgrade", 
            "pip", "setuptools", "wheel", "dynaconf"
        ])
    else:
        py = _resolve_python(cfg.preferred_python)
        if not py:
            raise RuntimeError(f"No suitable python interpreter {cfg.preferred_python} found for venv")
        logger.info("Creating %s with %s -m venv", cfg.path, py)
        subprocess.check_call([py, "-m", "venv", str(cfg.path)])
        
        # Use venv pip only if uv not available
        pip = cfg.path / "bin" / "pip"
        if not pip.exists():
            raise RuntimeError(f"pip not found in created venv: {pip}")
        subprocess.check_call([str(pip), "install", "-q", "--upgrade", "pip", "setuptools", "wheel", "dynaconf"])


def reexec_into_ci_venv(cfg: VenvConfig) -> None:
    # Replace current process with the CI venv Python interpreter. We set
    # HSF_IN_CI_VENV so downstream code knows it is running in the venv.
    py = str(cfg.path / "bin" / "python")
    os.environ["HSF_IN_CI_VENV"] = "1"
    os.execv(py, [py, *sys.argv])


def ensure_ci_venv_and_reexec(defaults: dict | None = None) -> Tuple[Path, Path]:
    """
    CRITICAL: Ensure CI runs in a virtual environment, NOT system Python.
    
    This function:
    1. Creates .venv-ci if it doesn't exist (using system Python ONLY for this)
    2. Re-executes the current script inside .venv-ci
    3. Returns venv path and bin directory for tool access
    
    SAFEGUARDS:
    - After venv creation, ALL operations MUST use venv Python
    - System Python is NEVER used for pip installations
    - All CI scripts inherit the venv Python automatically
    """
    defaults = defaults or load_defaults_yaml()
    apply_defaults_env(defaults)
    venv_name = os.environ.get("HSF_CI_VENV", ".venv-ci")
    preferred = os.environ.get("HSF_PREFERRED_PYTHON", "3.11")
    minimum = os.environ.get("HSF_MIN_PYTHON", "3.11")
    cfg = VenvConfig(path=PROJECT_ROOT / venv_name, preferred_python=preferred, min_python=minimum)
    logger = get_logger("hyperlib")
    
    # SAFEGUARD: Warn if running as root (common mistake in containers)
    if hasattr(os, 'geteuid') and os.geteuid() == 0 and not os.environ.get("HSF_ALLOW_ROOT"):
        logger.warning("Running as root! Set HSF_ALLOW_ROOT=1 to suppress this warning")
    
    if not running_in_ci_venv(cfg):
        if not cfg.path.exists():
            create_ci_venv(cfg, logger)
        reexec_into_ci_venv(cfg)
    
    # SAFEGUARD: Verify we're now in the venv
    if not running_in_ci_venv(cfg):
        logger.error("Failed to enter virtual environment!")
        sys.exit(1)
    
    return cfg.path, cfg.path / "bin"


# -------------------------- Runner helpers ---------------------------------

def list_sorted_scripts(dir_path: Path, patterns: Iterable[str]) -> List[Path]:
    scripts: List[Path] = []
    if not dir_path.exists():
        return scripts
    for p in dir_path.iterdir():
        if p.name.endswith(".disabled"):
            continue
        if any(p.name.endswith(pat) for pat in patterns):
            scripts.append(p)
    return sorted(scripts, key=lambda p: p.name)


def _platform_key() -> str:
    """Return platform key matching ci.yaml entries: macos, linux-apt, linux-dnf, windows."""
    if sys.platform == "darwin":
        return "macos"
    if sys.platform.startswith("win"):
        return "windows"
    
    # Detect Linux distro type
    if shutil.which("apt-get") or shutil.which("apt"):
        return "linux-apt"
    elif shutil.which("dnf") or shutil.which("yum"):
        return "linux-dnf"
    else:
        # Fallback to generic linux
        return "linux"


def _check_executable_available(name: str, root: Path) -> bool:
    """Check common places for the executable: PATH or node_modules/.bin."""
    if shutil.which(name):
        return True
    local_bin = root / "node_modules" / ".bin" / name
    if local_bin.exists():
        return True
    return False


def ensure_dependency(name: str, install: bool, logger: logging.Logger, defaults: dict | None = None) -> None:
    """Ensure a dependency `name` is available. If not and install=True,
    attempt to run installation commands from `ci.yaml` for this dependency
    for the current OS.

    The `ci.yaml` dependency structure is expected to be:

    dependencies:
      semantic-release:
        macos:
          - cmdline: "npm install -g semantic-release"
        linux:
          - cmdline: "npm install -g semantic-release"

    Each entry may contain multiple cmdline entries which will be executed
    in order until the dependency appears available.
    """
    defaults = defaults or load_defaults_yaml()
    if not isinstance(defaults, dict):
        defaults = {}
    deps = defaults.get("dependencies", {})
    if not isinstance(deps, dict):
        deps = {}
    entry = deps.get(name)
    root = PROJECT_ROOT
    if _check_executable_available(name, root):
        logger.info("Dependency %s already available", name)
        return

    if not entry:
        logger.error("No dependency mapping for %s in ci.yaml", name)
        if install:
            logger.warning("Install requested but no mapping found; cannot install %s", name)
            raise SystemExit(1)
        else:
            raise SystemExit(1)

    plat = _platform_key()
    candidates = entry.get(plat) or []
    if not candidates:
        # try generic 'all' key
        candidates = entry.get("all") or []

    if not candidates:
        logger.error("No install commands for %s on platform %s", name, plat)
        raise SystemExit(1)

    if not install:
        logger.error("Dependency %s missing and install not allowed", name)
        raise SystemExit(1)

    # Try executing cmdlines
    for item in candidates:
        cmd = None
        if isinstance(item, dict):
            cmd = item.get("cmdline")
        elif isinstance(item, str):
            cmd = item
        if not cmd:
            continue
        logger.info("Attempting install command for %s: %s", name, cmd)
        try:
            # run in shell to support complex install commands
            subprocess.check_call(cmd, shell=True)
        except Exception as exc:
            logger.warning("Install command failed: %s", exc)
        # check again
        if _check_executable_available(name, root):
            logger.info("Dependency %s available after install", name)
            return

    logger.error("Failed to install dependency %s; commands attempted", name)
    raise SystemExit(1)


def ensure_dependencies(names: Iterable[str], install: bool, logger: logging.Logger, defaults: dict | None = None) -> None:
    defaults = defaults or load_defaults_yaml()
    for n in names:
        ensure_dependency(n, install, logger, defaults)


