# Hyperlib - Project State

**Repository**: https://github.com/hypersec-io/hyperlib
**Type**: Python package (shared library)
**Purpose**: Enterprise infrastructure for all HyperSec Python projects
**Version**: 2.2.0 (see VERSION file)

---

## ⚠️ CRITICAL: Git Commit Rules

**⚠️ CRITICAL: TWO SEPARATE GIT REPOSITORIES**

**Hyperlib uses HyperCI as a git submodule at `/ci/`.**

This means there are **TWO completely separate git repositories**:
1. **Hyperlib repository** - `/projects/hyperlib/.git/` (main project)
2. **HyperCI repository** - `/projects/hyperlib/ci/.git/` (submodule)

**DO NOT CONFUSE THEM!**

### Commit to HyperCI Submodule (ci/ directory):

**CRITICAL:** All changes under `/ci/` MUST be committed to the **HyperCI repository**, not the hyperlib repository.

```bash
# For changes in ci/ directory:
cd ci
git add <files>
git commit -m "fix: description"
git push origin main

# Then update hyperlib to reference new ci/ commit:
cd ..
git add ci
git commit -m "chore: update ci submodule to <commit>"
git push origin main
```

**Files under `/ci/` go to:** https://github.com/hypersec-io/hyperci.git

**Important:**
- When you `cd ci`, you are in the HyperCI repository
- Git commands in ci/ affect the HyperCI repository ONLY
- Always `cd ..` back to hyperlib root before committing submodule reference

### Commit to Hyperlib (everything else):

**All other files** (src/, tests/, pyproject.toml, README.md, etc.) go to the hyperlib repository:

```bash
# For changes outside ci/ directory:
git add <files>
git commit -m "fix: description"
git push origin main
```

**Files outside `/ci/` go to:** https://github.com/hypersec-io/hyperlib.git

### Summary:

- ✅ `/ci/` → commit to hyperci submodule first, then update hyperlib
- ✅ Everything else → commit to hyperlib
- ❌ NEVER commit `/ci/` changes directly to hyperlib (they go to hyperci!)
- ⚠️ **TWO SEPARATE GIT REPOSITORIES** - do not confuse them!

---

## Quick Start

```bash
# Setup environment
./ci/bootstrap --install

# Run all checks
./ci/run check

# Build package
./ci/run build

# Create release (semantic versioning)
CI_PUSH=1 ./ci/run release
```

**Publishing**: Automatic via GitHub Actions on version tag push (`v*`)

---

## HyperCI Integration

**For complete CI documentation, see:**
- [ci/STATE.md](ci/STATE.md) - HyperCI infrastructure documentation
- [ci/docs/README.md](ci/docs/README.md) - Complete HyperCI guide
- [ci/docs/PYTHON.md](ci/docs/PYTHON.md) - Python-specific CI workflows
- [ci/docs/NUITKA.md](ci/docs/NUITKA.md) - Nuitka compilation guide
- [ci/docs/standards/CODE-ASSISTANT.md](ci/docs/standards/CODE-ASSISTANT.md) - AI assistant rules (CRITICAL)

**Quick reference:**
- Bootstrap: `./ci/bootstrap --install` (creates venvs, installs hooks)
- Test: `./ci/run check` (test + lint + type-check)
- Build: `./ci/run build` (wheel + sdist)
- Release: `CI_PUSH=1 ./ci/run release` (semantic versioning)
- AI setup: `CI_AI_MERGE_MODE=merge ./ci/ai setup` (Claude Code config)

---

## Project Overview

**Hyperlib** is a shared Python library providing enterprise infrastructure for all HyperSec Python projects.

- **Type**: Python package (publishable library)
- **Purpose**: Shared utilities (logging, config, bootstrap, caching, containers, timeouts)
- **Package name**: `hyperlib`
- **Repository**: https://github.com/hypersec-io/hyperlib
- **Published to**: JFrog Artifactory private PyPI
- **Version**: 2.2.0 (see VERSION file)

---

## Module Structure

```
hyperlib/
├── __init__.py       # Main exports: Application, get_logger, config utilities
├── application.py    # Primary user-facing API (Application class)
├── config.py         # Configuration management (get_logging_config, get_mount_config)
├── logger.py         # Structured logging (get_logger, setup, RFC 3339 timestamps)
├── harness.py        # Test harness and execution utilities
├── runtime.py        # Runtime paths and environment management
├── prometheus.py     # Prometheus metrics (create_metrics)
├── dbconn.py         # Database connection utilities
└── exceptions.py     # Custom exceptions
```

---

## Development Workflow

### 1. Make Changes

Edit code in `src/hyperlib/`, write tests in `tests/`.

### 2. Test Locally

```bash
./ci/run check      # All checks (test + lint + type-check)
./ci/run test       # Tests only
./ci/run build      # Build locally to verify
```

### 3. Commit with Conventional Commits

```bash
git add .
git commit -m "fix: improve error handling in Application.start()"
# Pre-commit hook auto-validates and syncs VERSION file
```

**Commit types:**
- `fix:` - Bug fix, improvement, refactor (patch bump) - **DEFAULT CHOICE**
- `feat:` - New significant feature (minor bump) - **RARELY USE**
- `perf:` - Performance optimization (patch bump)
- `chore:` - Maintenance, deps, config (no bump)
- `docs:` - Documentation only (no bump)
- `test:` - Tests only (no bump)

### 4. Create Release

```bash
# Preview next version
./ci/run release --dry-run

# Create release tag locally
FORCE_RELEASE=1 ./ci/run release

# Create release and push (triggers GitHub Actions)
FORCE_RELEASE=1 CI_PUSH=1 ./ci/run release
```

**Semantic versioning** is automatic based on commit types since last release.

### 5. Publish to JFrog

**Automatic**: GitHub Actions automatically builds and publishes on version tag push (`v*`).

**Manual** (discouraged):
```bash
./ci/run publish
```

---

## Version Management

- **Semantic versioning** via conventional commits
- **Git tags** are source of truth
- **VERSION file** auto-synced by pre-commit hook (prevents corruption)
- **pyproject.toml** and `__version__` auto-updated by semantic-release

**Current version:** 2.2.0

**Dual pre-sync strategy** prevents VERSION corruption:
- Pre-commit hook syncs VERSION before commit
- CI script (89-version-pre-sync.py) syncs before semantic-release
- Protects against `{version}` template corruption

---

## Testing

```bash
# Unit tests
pytest tests/

# Integration test (bootstrap from published package)
rm -rf ci-local/.venv .venv && ./ci/bootstrap --install
```

**Test coverage targets:**
- Minimum: 80% overall coverage
- Docstring coverage: 60% minimum

---

## Nuitka Builds (Optional)

Hyperlib supports **Nuitka Commercial** compilation for code protection.

**Build profiles:**
- `BUILD_PROFILE=package` (default): Standard Python wheel/sdist
- `BUILD_PROFILE=nuitka`: Nuitka-compiled standalone executable

**Protection levels:**
- `none`: Basic compilation only
- `minimal`: Standalone mode only
- `data-hiding`: Encrypt string constants and names
- `traceback`: Encrypt stdout/stderr and tracebacks
- `recommended` (default): Full protection stack

**Local build:**
```bash
BUILD_PROFILE=nuitka ./ci/run build
```

**GitHub Actions multi-arch build:**
- Automatic on version tag push (`v*`)
- Builds for x64 and ARM64 (if enabled in ci-local/ci.yaml)
- Cost-optimized runners (BuildJet, Cirrus)

See [ci/docs/NUITKA.md](ci/docs/NUITKA.md) for details.

---

## Publishing to JFrog

**⚠️ CRITICAL: Publishing is handled EXCLUSIVELY by GitHub Actions**

**Production workflow:**

1. **Local development**: Make changes and create version tag
   ```bash
   git add .
   git commit -m "feat: add new feature"
   FORCE_RELEASE=1 CI_PUSH=1 ./ci/run release  # Creates tag, pushes
   ```

2. **GitHub Actions**: Automatically triggered by version tag push
   - Workflow: `.github/workflows/jfrog-publish.yml`
   - Builds package fresh from source
   - Publishes to JFrog using GitHub Secrets

**Why GitHub Actions only?**
- **Security**: JFrog credentials only in GitHub Secrets
- **Auditability**: All publishes tracked in GitHub Actions logs
- **Consistency**: Same build process for everyone
- **Clean environment**: Fresh build every time

**JFrog authentication** (bootstrap only):
- Used ONLY for installing dependencies during bootstrap
- Credentials in `ci-local/.env` (gitignored)
- Variables: `ARTIFACTORY_USERNAME`, `ARTIFACTORY_PASSWORD`

---

## Role in Forge Ecosystem

Hyperlib serves two roles:

1. **Production library**: Shared utilities for all HyperSec Python projects
2. **Template validation**: Real-world test case for forge-python package template

Changes to hyperlib that affect template structure should be documented in `docs/TEMPLATE-CHANGES.md` for backporting to forge-python.

---

## Self-Contained Requirement

**CRITICAL**: Hyperlib MUST be completely self-contained with NO external file references.

- All code must work standalone
- No imports from parent directories
- No references to forge or other projects
- Bootstrap installs hyperlib from JFrog (published version)

---

## Bootstrap Paradox Resolution

Hyperlib's bootstrap installs hyperlib from JFrog, not from local source. This ensures:
1. Bootstrap works with minimal dependencies
2. Testing uses published package (real-world validation)
3. No circular dependencies
4. Consistent with all other projects

---

## Documentation

- **STATE.md** (this file) - Hyperlib-specific state and instructions
- **README.md** - User-facing documentation
- **TODO.md** - Task list
- **CHANGELOG.md** - Version history
- **ci/STATE.md** - HyperCI infrastructure documentation
- **ci/docs/** - Complete CI/CD documentation

---

**Last Updated:** 2025-10-28

---

## AI Assistant Guidance

**See [ci-local/CODE-ASSISTANT.md](ci-local/CODE-ASSISTANT.md) for bash usage and other AI assistant guidance.**

---

<!-- HYPERCI_STATE_MD: ci/modules/common/templates/STATE.md -->


---

<!-- HYPERCI_STATE_MD: HYPERCI_STATE_MD: ci/modules/python/templates/STATE.md -->
# HyperCI - Python CI/CD Documentation

**Auto-appended to project STATE.md during AI setup**

## Python CI Workflow (Quick Reference)

### Available Commands

**Testing:**
```bash
./ci/run check           # All checks (test + lint + type-check)
./ci/run test            # Tests only (pytest with coverage)
./ci/run dependency-update  # Update Python dependencies (uv lock)
```

**Building:**
```bash
./ci/run build           # Standard wheel + sdist (via uv build)
BUILD_PROFILE=nuitka ./ci/run build    # Nuitka compiled binary
```

**Releasing:**
```bash
./ci/run release --dry-run      # Preview next version
CI_PUSH=1 ./ci/run release      # Create release + push tag
```

**Publishing:**
```bash
./ci/run publish         # Build + publish to JFrog (manual, discouraged)
./ci/run verify-publish  # Verify package exists in JFrog
```

### Python-Specific Environment Variables

**Build Control:**
- `BUILD_PROFILE=package` - Standard wheel (default)
- `BUILD_PROFILE=nuitka` - Nuitka compiled binary
- `CI_BUILD_TYPE=standard` - Standard build (default)
- `CI_BUILD_TYPE=nuitka` - Nuitka build (alternative to BUILD_PROFILE)

**Nuitka Protection Levels:**
- `NUITKA_PROTECTION=none` - Basic compilation
- `NUITKA_PROTECTION=minimal` - Standalone mode only
- `NUITKA_PROTECTION=data-hiding` - Encrypt strings/names (Commercial)
- `NUITKA_PROTECTION=traceback` - Encrypt stdout/stderr (Commercial)
- `NUITKA_PROTECTION=recommended` - Full protection (default for Commercial)

**Testing:**
- `CI_COVERAGE_SOURCE` - Override coverage source directory
- `CI_VERIFY_PUBLISH=1` - Enable post-publish verification

**Release:**
- `CI_PUSH=1` - Push release commit and tag to remote
- `FORCE_RELEASE=1` - Force release even if not on release branch

### Python Module Scripts

**Bootstrap Scripts** (`ci/modules/python/bootstrap.d/`):
- `30-python-project.py` - Validate Python project structure
- `31-python-structure.py` - Create src/ layout if needed
- `32-jfrog.py` - Configure JFrog credentials
- `33-nuitka.py` - Check Nuitka requirements (if enabled)

**Runtime Scripts** (`ci/modules/python/run.d/`):
- `30-python-test.py` - Run pytest with coverage + ruff + mypy
- `31-python-dependency-update.py` - Update uv.lock dependencies
- `49-check-version-sync.py` - Check VERSION sync before release
- `50-build.py` - Build standard wheel/sdist
- `51-publish.py` - Publish to JFrog Artifactory
- `52-verify-publish.py` - Verify package exists in JFrog
- `55-build-nuitka.py` - Build Nuitka compiled binary
- `59-python-version-sync.py` - Sync VERSION across all files

### Dependencies

**Project deps:** `pyproject.toml` + `uv.lock` (project root)
**CI tool deps:** `ci-local/pyproject.toml` + `ci-local/uv.lock`

**Install:**
```bash
uv sync --locked                    # Install project deps
cd ci-local && uv sync --locked     # Install CI tools
```

**Update:**
```bash
./ci/run dependency-update          # Update project deps (uv lock)
cd ci-local && uv lock --upgrade    # Update CI tools
```

### Version Management

**VERSION file is auto-synced** by pre-commit hook (prevents corruption):
- Prevents `{version}` template corruption during semantic-release
- Dual protection: pre-commit hook + CI script (89-version-pre-sync.py)
- Synced across: VERSION, pyproject.toml, src/<package>/__init__.py

**Check sync:**
```bash
./ci/run check-version-sync
```

### GitHub Actions Integration

**Automatic builds** on version tag push (`v*`):
- Standard Python wheel published to JFrog
- Nuitka multi-arch builds (if `nuitka.enabled: true` in ci.yaml)
- Cost-optimized runners (BuildJet, Cirrus)

**Workflow:** `.github/workflows/jfrog-publish.yml`

---

**See also:** `ci/docs/PYTHON.md`, `ci/docs/NUITKA.md`, `ci/docs/TESTING.md`
