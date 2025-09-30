# Template Changes Required for forge-python

## Overview

This document tracks all issues, fixes, and improvements discovered while developing [hyperlib] that need to be backported to the `hypersec-forge-python` template.

As [hyperlib] serves as the real-world test case for the template, this ensures all learnings flow back to improve the template for future projects.

---

## Changes to Apply

### 1. Missing `__version__` in `__init__.py`

**Issue**: Generated projects don't export `__version__` attribute in their main `__init__.py`.

**Current State**:
```python
# Generated __init__.py has no __version__
from . import config
from . import logger
# ...
__all__ = ['config', 'logger', ...]
```

**Required Fix**:
```python
__version__ = "{{ version }}"  # Should be populated from copier context

# ... rest of imports ...

__all__ = ['config', 'logger', ..., '__version__']
```

**Template Files to Update**:
- `hypersec-forge-python: {{ package_name }}/__init__.py.jinja`

**Priority**: HIGH - Required for package distribution and version verification

---

### 2. Missing pytest markers configuration

**Issue**: Projects using pytest markers (like `@pytest.mark.e2e`) fail with "marker not found" error.

**Current State**: `pyproject.toml` has no `markers` list in `[tool.pytest.ini_options]`.

**Required Fix**:
```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = "-ra -q --strict-markers --cov={{ package_name }} --cov-report=term-missing"
pythonpath = ["src"]
markers = [
    "e2e: end-to-end integration tests",
    "integration: integration tests requiring external services",
    "slow: slow-running tests",
    "unit: fast unit tests",
]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]
```

**Template Files to Update**:
- `hypersec-forge-python: pyproject.toml.jinja`

**Priority**: MEDIUM - Breaks CI when using test markers

---

### 3. GitHub Workflow secrets configuration

**Issue**: Workflow template references `ARTIFACTORY_REPO_URL` secret that doesn't exist in organization secrets.

**Current State**:
```yaml
env:
  ARTIFACTORY_REPO_URL: ${{ secrets.ARTIFACTORY_REPO_URL }}
```

**Required Fix**: Hardcode the URL since it's already public throughout the codebase:
```yaml
env:
  ARTIFACTORY_REPO_URL: https://hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local
```

**Template Files to Update**:
- `subtrees/hypersec-forge-python/.github/workflows-disabled/pypi-publish.yml`
- Any other workflows referencing this secret

**Alternative**: Document that users should create this secret, but hardcoding is simpler.

**Priority**: HIGH - Blocks publishing workflow

---

### 4. Documentation structure

**Issue**: No `/docs` directory created in generated projects.

**Required Fix**: Template should create `docs/` directory with:
- `docs/ARTIFACTORY.md` - JFrog configuration for this project
- `docs/DEVELOPMENT.md` - Development setup and workflow
- `docs/DEPLOYMENT.md` - Deployment instructions (for libraries)
- `docs/API.md` - API documentation (for APIs/libraries)

**Template Files to Update**:
- Add `{{ package_name }}/docs/` directory structure
- Add documentation templates

**Priority**: MEDIUM - Improves project documentation

---

### 5. LICENSE file format (Setuptools deprecation warning)

**Issue**: Build produces warnings about deprecated license format:
```
SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
```

**Current State**:
```toml
[project]
license = {text = "HyperSec EULA"}
```

**Required Fix** (for setuptools >= 77.0.0):
```toml
[project]
license = "LicenseRef-HyperSec-EULA"  # SPDX expression for proprietary

# And remove classifier:
# "License :: Other/Proprietary License"  # Remove this
```

**Note**: May need to wait for setuptools 77.0.0 or add conditional logic.

**Template Files to Update**:
- `hypersec-forge-python: pyproject.toml.jinja`

**Priority**: LOW - Just a warning, doesn't break functionality

---

### 6. Bootstrap and CI configuration

**Issue**: Generated projects don't have clear CI execution instructions.

**Required Fix**: Ensure generated projects include:
- `scripts/bootstrap` wrapper that sets up `.venv-ci`
- `scripts/ci` wrapper for running CI locally
- Clear `README.md` section on running CI

**Template Files to Update**:
- Verify `scripts/bootstrap` is in template
- Verify `scripts/ci` is in template
- Add CI instructions to `README.md.jinja`

**Priority**: MEDIUM - Improves developer experience

---

### 7. Missing DEPLOYMENT.md for library projects

**Issue**: Library-type projects need deployment documentation but template doesn't generate it.

**Required Fix**: When `project_type == "library"`, generate:
- `DEPLOYMENT.md` with publishing instructions
- Version management guidelines
- Release process documentation

**Template Files to Update**:
- Add conditional `DEPLOYMENT.md.jinja` for library projects
- Link from main `README.md.jinja`

**Priority**: MEDIUM - Essential for library publishing workflow

---

### 8. Noxfile configuration error

**Issue**: Noxfile tries to set `nox.options.no_venv` which doesn't exist in newer nox versions, causing AttributeError.

**Current State**:
```python
if os.environ.get("HSF_IN_CI_VENV") == "1":
    nox.options.reuse_existing_virtualenvs = True
    nox.options.no_venv = True  # This attribute doesn't exist!
```

**Also problematic**: Sessions check `nox.options.no_venv` which also fails.

**Required Fix**:
```python
# In noxfile preamble
if os.environ.get("HSF_IN_CI_VENV") == "1":
    nox.options.reuse_existing_virtualenvs = True
    # Don't set no_venv here, use --no-venv flag instead

# In each session
@nox.session
def tests(session: nox.Session) -> None:
    """Run tests with pytest and coverage."""
    # Check environment variable instead of nox.options
    if os.environ.get("HSF_IN_CI_VENV") != "1":
        session.install("pytest", "pytest-cov", "-e", ".")
    session.run("pytest", "--cov", "--cov-report=term-missing")
```

**Usage in CI**:
```bash
export HSF_IN_CI_VENV=1
nox --no-venv -s tests  # Pass flag instead of setting option
```

**Template Files to Update**:
- `hypersec-forge-python: noxfile.py.jinja`

**Priority**: HIGH - Breaks nox in CI environments

---

### 9. Bootstrap doesn't create developer .venv

**Issue**: Bootstrap only creates `.venv-ci` for CI tools, not `.venv` for development work.

**Current State**:
- `.venv-ci` is created and populated with CI tools (nox, ruff, black, mypy, pytest, etc.) ✅
- `.venv` must be created manually by developers ❌
- Poor first-time developer experience

**Impact**:
Developers must manually run:
```bash
python -m venv .venv
.venv/bin/pip install -e .[dev]
```

**Required Fix**:
Add function to `bootstrap.d/20-python-dev-tools.py`:
```python
def ensure_dev_venv(root: Path, install: bool) -> None:
    """Create and populate developer .venv with project dependencies."""
    venv = root / ".venv"

    if not venv.exists():
        if not install:
            logger.warning(".venv does not exist (run with --install to create)")
            return

        logger.info("Creating developer .venv")
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)

    if install and (root / "pyproject.toml").exists():
        logger.info("Installing project in editable mode with dev dependencies")
        pip_path = venv / "bin" / "pip"

        # Install project with dev extras if available
        try:
            subprocess.run([
                str(pip_path), "install", "-e", ".[dev]", "-q"
            ], check=True)
            logger.success("Developer .venv ready")
        except subprocess.CalledProcessError:
            # Fallback: try without dev extras
            logger.warning("No [dev] extras found, installing base package")
            subprocess.run([
                str(pip_path), "install", "-e", ".", "-q"
            ], check=True)

# Call in main():
def main():
    # ... existing code ...
    ensure_dev_venv(root, install)  # Add this call
```

**Benefits**:
- First-time setup is complete after `./scripts/bootstrap --install`
- Developers can immediately start working
- Consistent setup across team
- `.venv` for development, `.venv-ci` for CI (proper isolation)

**Template Files to Update**:
- `hypersec-forge-python: scripts/bootstrap.d/20-python-dev-tools.py`

**Priority**: MEDIUM - Improves developer experience significantly

**Note**: Should also update README to document:
- `.venv` - Development environment (project dependencies)
- `.venv-ci` - CI environment (testing/linting tools)

---

## Verification Checklist

When applying changes back to template, verify:

- [ ] Generate a new test project from template
- [ ] Build package: `python -m build`
- [ ] Run tests: `pytest tests/`
- [ ] Verify `__version__` is accessible: `python -c "import pkg; print(pkg.__version__)"`
- [ ] Run CI: `./scripts/ci`
- [ ] Test GitHub workflow (if applicable)
- [ ] Check all documentation is generated
- [ ] Verify no deprecation warnings during build

---

## Application Process

1. **Create feature branch** in forge repository:
   ```bash
   git checkout -b feat/no-ref/apply-hyperlib-learnings
   ```

2. **Apply each change** to template files in the forge repository

3. **Test changes**:
   ```bash
   # Generate test project using forge
   hypersec-forge init --type python --name test-apply --dest /path/to/test-apply

   # Test build and CI
   cd test-apply
   ./scripts/bootstrap
   python -m build
   pytest tests/
   ```

4. **Update this document** as changes are applied (mark completed items)

5. **Commit with conventional commits**:
   ```bash
   git add subtrees/hypersec-forge-python
   git commit -m "fix(template): add __version__ export to __init__.py

   - Ensures generated packages export __version__ attribute
   - Required for package distribution and version verification
   - Discovered during hyperlib development"
   ```

6. **Push and create PR** for review

---

## Completed Changes

<!-- Move items here as they are applied and verified -->

None yet - all pending application to template.

---

## Future Enhancements

Items that aren't bugs but could improve the template:

### A. Enhanced test structure

Add more comprehensive test examples:
- Unit tests with fixtures
- Integration tests with markers
- Mock examples for external dependencies
- Coverage configuration examples

### B. Pre-commit hooks configuration

Include sensible pre-commit configuration:
- ruff (linting and formatting)
- mypy (type checking)
- vermin (Python version compatibility)
- conventional commits

### C. Nox sessions

Provide more nox sessions out of the box:
- `nox -s tests` - Run test suite
- `nox -s lint` - Run all linters
- `nox -s format` - Format code
- `nox -s build` - Build package
- `nox -s publish` - Publish to Artifactory

### D. Development container support

Add `.devcontainer/` configuration for consistent development environments.

### E. API documentation with Sphinx

For library projects, include:
- Sphinx configuration
- Auto-API documentation setup
- GitHub Pages deployment workflow

---

## Notes

- This document should be updated continuously as we discover issues
- Each entry should include: issue, current state, fix, affected files, priority
- Mark items as completed when applied to template and verified
- Use this as reference when updating template after hyperlib stabilizes

## Related Documentation

- [Hyperlib Deployment Guide](../DEPLOYMENT.md)
- [Hyperlib Artifactory Configuration](ARTIFACTORY.md)