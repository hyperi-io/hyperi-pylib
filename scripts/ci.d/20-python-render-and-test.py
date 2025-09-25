#!/usr/bin/env python3
"""
Python template CI step: render template and run comprehensive tests.

This script:
1. Renders the template with Copier to avoid parsing unrendered Jinja
2. Runs nox sessions (tests, lint, type) if available
3. Falls back to direct tool execution (pytest, ruff, black, mypy)
4. Runs security checks (bandit, safety, pip-audit)
5. Uses tools from .venv-ci for consistent versions
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Import hyperlib (in generated projects it's at scripts/hyperlib)
THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))
from hyperlib import get_logger  # type: ignore


def has_command(cmd: str) -> bool:
    """Check if command is available."""
    return shutil.which(cmd) is not None


def ensure_copier() -> str:
    """Find available copier command."""
    if has_command("copier"):
        return "copier"
    if has_command("uv"):
        return "uv run copier"
    if has_command("python"):
        return "python -m copier"
    raise RuntimeError("No copier available (tried: copier, uv run copier, python -m copier)")


def render_template_for_testing(root_dir: Path, logger) -> Path:
    """Render template to .tmp/run for CI checks to avoid parsing unrendered Jinja."""
    render_dir = root_dir / ".tmp" / "run"
    if render_dir.exists():
        shutil.rmtree(render_dir)
    render_dir.mkdir(parents=True)
    
    try:
        copier_cmd = ensure_copier()
        logger.info("Rendering via: %s", copier_cmd)
        
        cmd = copier_cmd.split() + [
            "-f",
            "-d", "project_name=testproject",
            "-d", "package_name=testproject", 
            "-d", "description=Test",
            "-d", "author_name=Tester",
            "-d", "author_email=tester@example.com",
            "-d", "github_org=hypersec-io",
            "-d", "license=hypersec-eula",
            "-r", "HEAD",
            str(root_dir),
            str(render_dir)
        ]
        
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL)
        logger.info("Template rendered successfully")
        return render_dir
        
    except Exception as e:
        logger.warning("Copier failed (%s), using rsync fallback", e)
        # Fallback: rsync (may fail with Jinja tokens)
        subprocess.check_call([
            "rsync", "-a", 
            "--exclude", ".git",
            "--exclude", ".tmp", 
            "--exclude", ".venv",
            str(root_dir) + "/",
            str(render_dir) + "/"
        ])
        return render_dir


def run_nox_sessions(render_dir: Path, venv_prefix: str, logger) -> bool:
    """Run nox sessions if available."""
    nox_cmd = f"{venv_prefix}nox"
    if not Path(nox_cmd).exists():
        return False
    
    try:
        # When running from .venv-ci, use --no-venv for speed
        nox_args = [nox_cmd, "-s", "tests", "-s", "lint", "-s", "type"]
        if os.environ.get("HSF_IN_CI_VENV") == "1":
            logger.info("Running nox sessions with --no-venv (reusing .venv-ci)")
            nox_args.append("--no-venv")
        else:
            logger.info("Running nox sessions: tests, lint, type")
        
        # Set environment to avoid color flag conflicts
        env = os.environ.copy()
        env.pop("NO_COLOR", None)
        subprocess.check_call(nox_args, cwd=render_dir, env=env)
        logger.info("Nox sessions passed")
        return True
    except subprocess.CalledProcessError:
        logger.error("Nox sessions failed")
        raise


def run_direct_tools(render_dir: Path, venv_prefix: str, logger) -> None:
    """Run tools directly if nox not available."""
    logger.warning("Nox not found; using direct tools")
    
    # Tests
    tests_dir = render_dir / "tests"
    if tests_dir.exists():
        pytest_cmd = f"{venv_prefix}pytest"
        if Path(pytest_cmd).exists():
            logger.info("Running pytest from .venv-ci")
            try:
                subprocess.check_call([pytest_cmd, "-q"], cwd=render_dir)
                logger.info("Pytest passed")
            except subprocess.CalledProcessError as e:
                if e.returncode == 5:
                    logger.warning("No tests collected")
                else:
                    logger.error("Pytest failed (rc=%d)", e.returncode)
                    raise
        elif has_command("pytest"):
            logger.warning("Using system pytest (no .venv-ci)")
            try:
                subprocess.check_call(["pytest", "-q"], cwd=render_dir)
                logger.info("Pytest passed")
            except subprocess.CalledProcessError as e:
                if e.returncode == 5:
                    logger.warning("No tests collected")
                else:
                    logger.error("Pytest failed (rc=%d)", e.returncode)
                    raise
        else:
            logger.warning("Pytest not found; skipping tests")
    else:
        logger.warning("No tests directory; skipping tests")
    
    # Linting
    ruff_cmd = f"{venv_prefix}ruff"
    if Path(ruff_cmd).exists():
        logger.info("Running ruff from .venv-ci")
        subprocess.check_call([ruff_cmd, "check", "."], cwd=render_dir)
        logger.info("Ruff passed")
    elif has_command("ruff"):
        logger.warning("Using system ruff")
        subprocess.check_call(["ruff", "check", "."], cwd=render_dir)
        logger.info("Ruff passed")
    
    # Formatting
    black_cmd = f"{venv_prefix}black"
    if Path(black_cmd).exists():
        logger.info("Running black from .venv-ci")
        subprocess.check_call([black_cmd, "--check", "."], cwd=render_dir)
        logger.info("Black check passed")
    elif has_command("black"):
        logger.warning("Using system black")
        subprocess.check_call(["black", "--check", "."], cwd=render_dir)
        logger.info("Black check passed")
    
    # Type checking
    mypy_cmd = f"{venv_prefix}mypy"
    if Path(mypy_cmd).exists():
        logger.info("Running mypy from .venv-ci")
        subprocess.check_call([mypy_cmd, "."], cwd=render_dir)
        logger.info("Mypy passed")
    elif has_command("mypy"):
        logger.warning("Using system mypy")
        subprocess.check_call(["mypy", "."], cwd=render_dir)
        logger.info("Mypy passed")


def run_security_checks(render_dir: Path, venv_prefix: str, logger) -> None:
    """Run security analysis tools."""
    
    # Safety check
    safety_cmd = f"{venv_prefix}safety"
    if Path(safety_cmd).exists():
        logger.info("Running security checks (safety)")
        subprocess.check_call([safety_cmd, "check"], cwd=render_dir)
        logger.info("Safety passed")
    else:
        logger.warning("Safety not found; skipping security check")
    
    # Package audit
    pip_audit_cmd = f"{venv_prefix}pip-audit"
    if Path(pip_audit_cmd).exists():
        logger.info("Running package audit (pip-audit)")
        subprocess.check_call([pip_audit_cmd, "-s", "pip"], cwd=render_dir)
        logger.info("Pip-audit passed")
    else:
        logger.warning("Pip-audit not found; skipping package audit")
    
    # Static security analysis
    bandit_cmd = f"{venv_prefix}bandit"
    if Path(bandit_cmd).exists():
        logger.info("Running static security analysis (bandit)")
        # Run against src directory if present, else project root
        target_dir = "src" if (render_dir / "src").exists() else "."
        subprocess.check_call([bandit_cmd, "-r", target_dir, "-ll"], cwd=render_dir)
        logger.info("Bandit passed")
    else:
        logger.warning("Bandit not found; skipping static security analysis")


def main() -> int:
    logger = get_logger("python-ci")
    root_dir = Path.cwd()
    
    # Assume .venv-ci has been created by core bootstrap
    venv_ci = root_dir / ".venv-ci"
    if not venv_ci.exists():
        logger.error(".venv-ci missing. Core CI should run bootstrap with installs first.")
        return 1
    
    venv_prefix = str(venv_ci / "bin") + "/"
    
    # Render template for testing
    try:
        render_dir = render_template_for_testing(root_dir, logger)
    except Exception as e:
        logger.error("Failed to render template: %s", e)
        return 1
    
    # Change to rendered directory for tests
    original_cwd = Path.cwd()
    try:
        import os
        os.chdir(render_dir)
        logger.info("Running Python checks in rendered project: %s", render_dir)
        
        # Try nox first, fall back to direct tools
        if run_nox_sessions(render_dir, venv_prefix, logger):
            logger.info("Nox sessions completed successfully")
        else:
            run_direct_tools(render_dir, venv_prefix, logger)
        
        # Run security checks
        run_security_checks(render_dir, venv_prefix, logger)
        
        logger.info("Python template CI step complete")
        return 0
        
    except subprocess.CalledProcessError as e:
        logger.error("CI step failed with exit code %d", e.returncode)
        return e.returncode
    except Exception as e:
        logger.error("CI step failed: %s", e)
        return 1
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    sys.exit(main())
