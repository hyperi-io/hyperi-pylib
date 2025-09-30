"""Nox configuration optimized for .venv-ci usage.

By default, nox creates isolated virtualenvs for each session.
For CI, we optimize by reusing the existing .venv-ci environment.

Usage:
- Developer: `nox` (creates isolated envs for safety)
- CI: `nox --no-venv` (reuses .venv-ci for speed)
"""
import os
import nox

# Optimize for CI when HSF_IN_CI_VENV is set (set by hyperlib re-exec)
if os.environ.get("HSF_IN_CI_VENV") == "1":
    # When running in .venv-ci, reuse it instead of creating new venvs
    nox.options.reuse_existing_virtualenvs = True
    # Use --no-venv flag instead of setting option here

@nox.session
def tests(session: nox.Session) -> None:
    """Run tests with pytest and coverage."""
    # In CI (HSF_IN_CI_VENV=1), dependencies are already in .venv-ci
    if os.environ.get("HSF_IN_CI_VENV") != "1":
        session.install("pytest", "pytest-cov", "-e", ".")
    session.run("pytest", "--cov", "--cov-report=term-missing")

@nox.session
def lint(session: nox.Session) -> None:
    """Run linters (ruff and black in check mode)."""
    if os.environ.get("HSF_IN_CI_VENV") != "1":
        session.install("ruff", "black")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")

@nox.session
def format(session: nox.Session) -> None:
    """Format code with ruff and black."""
    if os.environ.get("HSF_IN_CI_VENV") != "1":
        session.install("ruff", "black")
    session.run("ruff", "check", "--fix", ".")
    session.run("black", ".")

@nox.session
def type(session: nox.Session) -> None:
    """Type check with mypy."""
    if os.environ.get("HSF_IN_CI_VENV") != "1":
        session.install("mypy", "-e", ".")
    session.run("mypy", ".")

@nox.session
def security(session: nox.Session) -> None:
    """Run security checks with bandit, safety, and pip-audit."""
    if os.environ.get("HSF_IN_CI_VENV") != "1":
        session.install("bandit[toml]", "safety", "pip-audit")
    session.run("bandit", "-r", "src/")
    session.run("safety", "check")
    session.run("pip-audit")

@nox.session(python=["3.11", "3.12"])
def test_versions(session: nox.Session) -> None:
    """Test against multiple Python versions (for libraries)."""
    session.install("pytest", "pytest-cov", "-e", ".")
    session.run("pytest", "--cov")
