#!/usr/bin/env python3
"""Bootstrap entrypoint - installs hyperlib from JFrog before importing it.

Usage:
- `scripts/bootstrap` (default): Check-only mode, verify tools are present
- `scripts/bootstrap --install`: Enable installation of missing tools

CRITICAL SAFEGUARDS:
- This script MUST run in a virtual environment (.venv-ci)
- System Python is ONLY used for initial venv creation
- All pip installations MUST target .venv-ci
- NO operations should use system Python after venv creation

Three-phase bootstrap process:
1. Phase 0: Create .venv-ci if needed (system Python)
2. Phase 1: Install hyperlib from JFrog (venv Python)
3. Phase 2: Import hyperlib and run bootstrap.d scripts (venv Python)
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent


def load_dotenv_minimal() -> None:
    """Minimal .env loader without external dependencies."""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        return

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


def is_in_venv() -> bool:
    """Check if we're running inside a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )


def create_venv_if_needed(venv_dir: Path) -> bool:
    """Create .venv-ci if it doesn't exist. Returns True if created."""
    if venv_dir.exists():
        return False

    print(f"[INFO] Creating {venv_dir}...")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    return True


def get_jfrog_index_url() -> str:
    """Get JFrog PyPI index URL with credentials from environment."""
    jf_user = os.environ.get("JF_USER", "")
    jf_password = os.environ.get("JF_PASSWORD", "")

    base_url = "https://hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local/simple"

    if jf_user and jf_password:
        # URL-encode credentials
        from urllib.parse import quote
        user_enc = quote(jf_user, safe='')
        pass_enc = quote(jf_password, safe='')
        return f"https://{user_enc}:{pass_enc}@hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local/simple"

    return base_url


def install_hyperlib(venv_python: Path) -> None:
    """Install hyperlib from JFrog Artifactory into .venv-ci."""
    try:
        # Check if hyperlib is already installed
        result = subprocess.run(
            [str(venv_python), "-c", "import hyperlib; print(hyperlib.__version__)"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"[INFO] hyperlib {version} already installed")
            return
    except Exception:
        pass

    print("[INFO] Installing hyperlib from JFrog Artifactory...")

    jfrog_url = get_jfrog_index_url()

    # Install hyperlib with fallback to PyPI if JFrog unavailable
    try:
        subprocess.check_call(
            [str(venv_python), "-m", "pip", "install", "hyperlib",
             "--extra-index-url", jfrog_url,
             "--quiet"],
            stderr=subprocess.STDOUT
        )
        print("[OK] hyperlib installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Failed to install hyperlib from JFrog: {e}")
        print("[INFO] Hyperlib may not be published yet - check JFrog credentials")
        sys.exit(1)


def reexec_in_venv(venv_python: Path) -> None:
    """Re-exec this script using the venv Python."""
    os.environ["HSF_IN_CI_VENV"] = "1"
    os.execv(str(venv_python), [str(venv_python)] + sys.argv)


def main() -> int:
    """Bootstrap entrypoint."""
    parser = argparse.ArgumentParser(description="Bootstrap development environment")
    parser.add_argument("--install", action="store_true",
                       help="Install missing tools (default: check-only)")
    args = parser.parse_args()

    # Load .env file early
    load_dotenv_minimal()

    # Set environment variable based on CLI flag
    if args.install:
        os.environ["BOOTSTRAP_INSTALL"] = "1"
    else:
        os.environ.setdefault("BOOTSTRAP_INSTALL", "0")

    # Phase 0: Ensure .venv-ci exists
    venv_name = os.environ.get("HSF_CI_VENV", ".venv-ci")
    venv_dir = PROJECT_ROOT / venv_name
    venv_python = venv_dir / "bin" / "python"

    # If not in venv yet, create it and re-exec
    if not os.environ.get("HSF_IN_CI_VENV"):
        create_venv_if_needed(venv_dir)

        # Phase 1: Install hyperlib from JFrog
        install_hyperlib(venv_python)

        # Re-exec in venv
        reexec_in_venv(venv_python)
        # Should never reach here
        return 1

    # Phase 2: Now we're in venv with hyperlib installed
    # Import hyperlib and run bootstrap steps
    sys.path.insert(0, str(THIS_DIR))

    try:
        from hyperlib import get_logger, list_sorted_scripts, load_defaults_yaml, ensure_dependency, load_dotenv  # type: ignore
    except ImportError as e:
        print(f"[ERR] Failed to import hyperlib: {e}")
        print("[INFO] Hyperlib should have been installed in Phase 1")
        return 1

    # Reload .env with hyperlib's full implementation
    load_dotenv()

    logger = get_logger("bootstrap")
    logger.info("Running bootstrap in .venv-ci")

    boot_dir = PROJECT_ROOT / "scripts" / "bootstrap.d"
    scripts = list_sorted_scripts(boot_dir, patterns=(".sh", ".py"))
    if not scripts:
        logger.info("No bootstrap steps found at %s", boot_dir)
        return 0

    install = os.environ.get("BOOTSTRAP_INSTALL", "0") == "1"

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
            subprocess.check_call([str(venv_python), str(path), "check"])
        if install:
            logger.info("Bootstrap install: %s", base)
            if base.endswith(".sh"):
                subprocess.check_call(["bash", str(path), "install"])
            elif base.endswith(".py"):
                subprocess.check_call([str(venv_python), str(path), "install"])

    logger.info("Bootstrap complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())