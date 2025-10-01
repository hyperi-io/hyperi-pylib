#!/usr/bin/env python3
"""
Deploy Package - Publish distributions to JFrog Artifactory.

Actions:
- check: Verify deployment dependencies and credentials
- install: Install deployment dependencies (twine)
- deploy: Build and publish to JFrog Artifactory

Environment Variables:
- JF_USER or ARTIFACTORY_USERNAME: JFrog username
- JF_PASSWORD or ARTIFACTORY_PASSWORD: JFrog password
- ARTIFACTORY_URL: JFrog Artifactory URL (default: hypersec.jfrog.io)
"""

import os
import subprocess
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Setup Python path for hyperlib imports
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from hyperlib import get_logger  # type: ignore

logger = get_logger("deploy")

# JFrog Artifactory configuration
ARTIFACTORY_URL = os.environ.get(
    "ARTIFACTORY_URL",
    "https://hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local"
)


def get_credentials() -> tuple:
    """Get JFrog credentials from environment."""
    username = os.environ.get("JF_USER") or os.environ.get("ARTIFACTORY_USERNAME")
    password = os.environ.get("JF_PASSWORD") or os.environ.get("ARTIFACTORY_PASSWORD")
    return username, password


def check_action(logger) -> int:
    """Check if deployment is possible."""
    venv_python = PROJECT_ROOT / ".venv-ci" / "bin" / "python"
    if not venv_python.exists():
        logger.error(".venv-ci not found. Run: ./scripts/bootstrap --install")
        return 1

    # Check if twine is available
    result = subprocess.run(
        [str(venv_python), "-c", "import twine"],
        capture_output=True
    )
    if result.returncode != 0:
        logger.error("twine not available")
        logger.info("Install with: .venv-ci/bin/pip install twine")
        return 1

    # Check credentials
    username, password = get_credentials()
    if not username or not password:
        logger.error("JFrog credentials not found")
        logger.info("Set JF_USER and JF_PASSWORD environment variables")
        return 1

    logger.info("✓ Deployment dependencies available")
    logger.info(f"  Username: {username}")
    logger.info(f"  URL: {ARTIFACTORY_URL}")
    return 0


def install_action(logger) -> int:
    """Install deployment dependencies."""
    venv_python = PROJECT_ROOT / ".venv-ci" / "bin" / "python"
    if not venv_python.exists():
        logger.error(".venv-ci not found. Run: ./scripts/bootstrap --install")
        return 1

    logger.info("Installing deployment dependencies...")
    result = subprocess.run(
        [str(venv_python), "-m", "pip", "install", "twine"],
        cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        logger.error("Failed to install twine")
        return 1

    logger.info("✓ Deployment dependencies installed")
    return 0


def deploy_action(logger) -> int:
    """Deploy package to JFrog Artifactory."""
    venv_python = PROJECT_ROOT / ".venv-ci" / "bin" / "python"
    if not venv_python.exists():
        logger.error(".venv-ci not found. Run: ./scripts/bootstrap --install")
        return 1

    # Check credentials
    username, password = get_credentials()
    if not username or not password:
        logger.error("JFrog credentials not found")
        logger.info("Set JF_USER and JF_PASSWORD environment variables")
        return 1

    # Check if dist/ exists and has files
    dist_dir = PROJECT_ROOT / "dist"
    if not dist_dir.exists() or not list(dist_dir.iterdir()):
        logger.info("No distributions found. Building package first...")
        # Run build
        result = subprocess.run(
            [str(venv_python), str(PROJECT_ROOT / "scripts" / "ci.d" / "80-build.py"), "build"],
            cwd=PROJECT_ROOT
        )
        if result.returncode != 0:
            logger.error("Build failed")
            return 1

    # Upload to JFrog
    logger.info("Uploading to JFrog Artifactory...")
    logger.info(f"  URL: {ARTIFACTORY_URL}")

    env = os.environ.copy()
    env["TWINE_USERNAME"] = username
    env["TWINE_PASSWORD"] = password

    result = subprocess.run(
        [
            str(venv_python), "-m", "twine", "upload",
            "--repository-url", ARTIFACTORY_URL,
            "dist/*"
        ],
        cwd=PROJECT_ROOT,
        env=env
    )
    if result.returncode != 0:
        logger.error("Upload failed")
        return 1

    logger.info("✓ Package deployed successfully")
    return 0


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        logger.error("Usage: %s [check|install|deploy|release]", sys.argv[0])
        return 1

    action = sys.argv[1]

    if action == "check":
        return check_action(logger)
    elif action == "install":
        return install_action(logger)
    elif action in ["deploy", "release"]:
        return deploy_action(logger)
    else:
        # Unknown action - skip silently (other scripts may handle it)
        return 0


if __name__ == "__main__":
    sys.exit(main())
