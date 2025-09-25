#!/usr/bin/env python3
"""Python development tools bootstrap script.

Manages Python-specific development and CI tools installation.
Creates project .venv for development and populates .venv-ci with CI tools.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple

# Add hyperlib to path if available
scripts_dir = Path(__file__).parent.parent
hyperlib_path = scripts_dir / "hyperlib"
if hyperlib_path.exists():
    sys.path.insert(0, str(scripts_dir))
    try:
        from hyperlib import logger
    except ImportError:
        # Fallback to basic logging
        class Logger:
            def info(self, msg): print(f"[INFO] {msg}")
            def success(self, msg): print(f"[OK] {msg}")
            def warning(self, msg): print(f"[WARN] {msg}")
            def error(self, msg): print(f"[ERR] {msg}")
        logger = Logger()
else:
    # Fallback logging
    class Logger:
        def info(self, msg): print(f"[INFO] {msg}")
        def success(self, msg): print(f"[OK] {msg}")
        def warning(self, msg): print(f"[WARN] {msg}")
        def error(self, msg): print(f"[ERR] {msg}")
    logger = Logger()


# Python CI tools to install
PYTHON_CI_TOOLS = [
    "nox>=2024.0.0",
    "ruff>=0.1.0",
    "black>=24.0.0",
    "mypy>=1.8.0",
    "pytest>=8.0.0",
    "bandit[toml]>=1.7.0",
    "safety>=3.0.0",
    "pip-audit>=2.6.0",
    "vermin>=1.6.0",
]

TOOL_NAMES = ["nox", "ruff", "black", "mypy", "pytest", "bandit", "safety", "pip-audit", "vermin"]


def has_command(cmd: str) -> bool:
    """Check if a command is available."""
    return shutil.which(cmd) is not None


def run_command(cmd: List[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a command with optional output capture."""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            raise
        return e


def install_missing_tools(venv_ci: Path) -> None:
    """Attempt to install missing Python tools into .venv-ci."""
    if not venv_ci.exists():
        return
    
    if has_command("uv"):
        logger.info("Installing missing Python tools into .venv-ci")
        cmd = ["uv", "pip", "install", "--python", str(venv_ci), "-q"] + PYTHON_CI_TOOLS
        result = run_command(cmd, check=False)
        if result.returncode != 0:
            logger.warning("Failed to install some tools")
    elif (venv_ci / "bin" / "pip").exists():
        logger.info("Installing missing Python tools into .venv-ci")
        cmd = [str(venv_ci / "bin" / "pip"), "install", "-q"] + PYTHON_CI_TOOLS
        result = run_command(cmd, check=False)
        if result.returncode != 0:
            logger.warning("Failed to install some tools")


def check_tool(tool: str, venv_ci: Path) -> bool:
    """Check if a tool is available in .venv-ci or system."""
    venv_tool = venv_ci / "bin" / tool
    if venv_tool.exists() and os.access(venv_tool, os.X_OK):
        logger.success(f"{tool} available in .venv-ci")
        return True
    elif has_command(tool):
        logger.success(f"{tool} available on system")
        return True
    else:
        logger.error(f"{tool} not found - required")
        return False


def check_action() -> int:
    """Check if all required Python tools are available."""
    venv_ci = Path(".venv-ci")
    
    # Try to install tools automatically if .venv-ci exists
    install_missing_tools(venv_ci)
    
    # Check for all tools
    missing = 0
    for tool in TOOL_NAMES:
        if not check_tool(tool, venv_ci):
            missing += 1
    
    return missing


def install_action() -> int:
    """Install Python development environment and CI tools."""
    project_root = Path.cwd()
    venv_path = project_root / ".venv"
    venv_ci_path = project_root / ".venv-ci"
    
    # Create project .venv for development
    if has_command("uv"):
        logger.info("Creating project .venv with uv")
        run_command(["uv", "venv", str(venv_path)], check=False)
        
        # Install development dependencies
        if (project_root / "pyproject.toml").exists():
            run_command(
                ["uv", "pip", "install", "--python", str(venv_path), "-e", ".[dev]"],
                check=False
            )
        
        # Install CI tools into .venv-ci
        logger.info("Installing CI tools into .venv-ci (managed by core bootstrap)")
        if venv_ci_path.exists():
            cmd = ["uv", "pip", "install", "--python", str(venv_ci_path), "-q"] + PYTHON_CI_TOOLS
            run_command(cmd, check=False)
            logger.info(".venv-ci populated with Python tools")
        else:
            logger.warning(".venv-ci not found; core bootstrap should create it first")
            
    elif has_command("python3"):
        logger.info("Creating project .venv with python3")
        run_command(["python3", "-m", "venv", str(venv_path)], check=False)
        
        # Upgrade pip
        pip_path = venv_path / "bin" / "pip"
        if pip_path.exists():
            run_command([str(pip_path), "install", "-q", "--upgrade", "pip"], check=False)
            
            # Install development dependencies
            if (project_root / "pyproject.toml").exists():
                run_command([str(pip_path), "install", "-q", "-e", ".[dev]"], check=False)
        
        # Install CI tools into .venv-ci if it exists
        if venv_ci_path.exists():
            ci_pip = venv_ci_path / "bin" / "pip"
            if ci_pip.exists():
                cmd = [str(ci_pip), "install", "-q"] + PYTHON_CI_TOOLS
                run_command(cmd, check=False)
                logger.info(".venv-ci populated with Python tools")
        else:
            logger.warning(".venv-ci not found; core bootstrap should create it first")
    else:
        logger.error("Cannot create project .venv: no uv or python3 available")
        return 1
    
    # Verify CI tools are available
    if venv_ci_path.exists():
        missing_tools = []
        for tool in TOOL_NAMES:
            tool_path = venv_ci_path / "bin" / tool
            if not tool_path.exists():
                missing_tools.append(tool)
        
        if missing_tools:
            logger.warning(f"Some CI tools missing in .venv-ci: {', '.join(missing_tools)}")
    
    return 0


def main():
    """Main entry point."""
    action = sys.argv[1] if len(sys.argv) > 1 else "check"
    
    if action == "check":
        exit_code = check_action()
    elif action == "install":
        exit_code = install_action()
    else:
        logger.error(f"Unknown action: {action} (expected: check|install)")
        exit_code = 2
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
