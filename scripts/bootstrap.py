#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
from hyperlib import get_logger, ensure_ci_venv_and_reexec, list_sorted_scripts, load_defaults_yaml, ensure_dependency  # type: ignore


def main() -> int:
    """Bootstrap entrypoint.

    Usage:
    - `scripts/bootstrap` (default): Check-only mode, verify tools are present
    - `scripts/bootstrap --install`: Enable installation of missing tools

    CRITICAL SAFEGUARDS:
    - This script MUST run in a virtual environment (.venv-ci)
    - System Python is ONLY used for initial venv creation
    - All pip installations MUST target .venv-ci
    - NO operations should use system Python after venv creation

    Relationship notes:
    - This script is responsible for ensuring a reproducible `.venv-ci` used
      by all later CI steps. It calls `ensure_ci_venv_and_reexec()` which will
      create the venv (if missing) and re-exec this process under
      `.venv-ci/bin/python`.

    - After re-exec we run all `scripts/bootstrap.d/*` scripts in sorted order.
      Each bootstrap child script must expose a `check` action and may
      optionally implement `install` (called when BOOTSTRAP_INSTALL=1).

    - The CI wrapper (`scripts/ci`) calls this bootstrap entrypoint before
      executing layered CI steps. Child CI scripts should assume tools are
      available in `.venv-ci/bin` and should not try to create the venv.

    Dependency notes:
    - The bootstrap verifies presence of `semantic-release` CLI (used by
      the release process). It will attempt installation commands from ci.yaml
      only when --install flag is used; otherwise it fails early to enforce
      the release toolchain.
    """
    parser = argparse.ArgumentParser(description="Bootstrap development environment")
    parser.add_argument("--install", action="store_true", 
                       help="Install missing tools (default: check-only)")
    args = parser.parse_args()
    
    # Set environment variable based on CLI flag
    if args.install:
        os.environ["BOOTSTRAP_INSTALL"] = "1"
    else:
        os.environ.setdefault("BOOTSTRAP_INSTALL", "0")
    
    logger = get_logger("bootstrap")
    ensure_ci_venv_and_reexec()

    root = THIS_DIR.parent
    boot_dir = root / "scripts" / "bootstrap.d"
    scripts = list_sorted_scripts(boot_dir, patterns=(".sh", ".py"))
    if not scripts:
        logger.info("No bootstrap steps found at %s", boot_dir)
        return 0

    install = os.environ.get("BOOTSTRAP_INSTALL", "0") == "1"
    venv_py = str((root / os.environ.get("HSF_CI_VENV", ".venv-ci") / "bin" / "python"))

    # Ensure semantic-release CLI is present (required)
    defaults = load_defaults_yaml()
    try:
        ensure_dependency("semantic-release", install, logger, defaults)
    except SystemExit:
        # ensure_dependency will have logged; re-raise to stop bootstrap
        raise

    for path in scripts:
        base = path.name
        if base.endswith(".disabled"):
            logger.info("Skipping disabled %s", base)
            continue
        logger.info("Bootstrap check: %s", base)
        if base.endswith(".sh"):
            subprocess.check_call(["bash", str(path), "check"])
        elif base.endswith(".py"):
            subprocess.check_call([venv_py, str(path), "check"]) if os.path.exists(venv_py) else subprocess.check_call([sys.executable, str(path), "check"])
        if install:
            logger.info("Bootstrap install: %s", base)
            if base.endswith(".sh"):
                subprocess.check_call(["bash", str(path), "install"])
            elif base.endswith(".py"):
                subprocess.check_call([venv_py, str(path), "install"]) if os.path.exists(venv_py) else subprocess.check_call([sys.executable, str(path), "install"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

