# Hyperlib - Project State

## CRITICAL: Read Documentation First

<!--
AI AGENTS: Read these files BEFORE starting work:
1. STATE.md (or CLAUDE.md symlink)
2. docs/CHARS-POLICY.md - Character restrictions (ASCII logs, limited emoji)
3. docs/CONTRIBUTING.md - Workflow and conventions
4. docs/DEVELOPMENT.md - Setup and build
5. README.md - Project overview
6. docs/ARTIFACTORY.md - JFrog publishing
-->

## Project Overview

**Hyperlib** is a shared Python library providing enterprise infrastructure for all HyperSec Python projects.

- **Type**: Python package (publishable library)
- **Purpose**: Shared utilities (logging, config, bootstrap, caching, containers, timeouts)
- **Package name**: `hyperlib`
- **Repository**: `https://github.com/hypersec-io/hyperlib`
- **Published to**: JFrog Artifactory private PyPI
- **Version**: 1.5.0 (see VERSION file)

## Bootstrap (ALWAYS Run First)

**Setup**: `./ci/bootstrap --install` | **Check**: `./ci/bootstrap`

**3 Phases**:
1. System Python creates `ci/.venv`
2. Installs `hyperlib` from JFrog Artifactory
3. Imports hyperlib, runs `bootstrap.d/*` scripts

**Requires**: `.env` with `JF_USER`/`JF_PASSWORD`, Python 3.11+, JFrog network access

**Installs**: `ci/.venv`, hyperlib (latest from JFrog), nox, pytest, ruff, black, mypy, twine, semantic-release

### Virtual Environment (CRITICAL - READ CAREFULLY)

**Two COMPLETELY SEPARATE environments exist. NEVER mix them!**

#### ci/.venv (CI/Automation ONLY)
- **Purpose**: ALL CI scripts, ALL automation, testing, building, releasing
- **Created by**: `./ci/bootstrap --install`
- **Contains**: hyperlib (from JFrog), CI tools (nox, pytest, ruff, etc.)
- **Marker file**: `ci/.venv/.THIS_IS_CI_VENV`
- **Env vars**: `VENV_PURPOSE=ci`, `VENV_TYPE=automation`
- **Usage**: NEVER activate manually, ALWAYS run via `./ci/ci <action>`
- **Python**: `ci/.venv/bin/python` (explicit path only)

#### .venv (Development ONLY)
- **Purpose**: IDE, manual testing, exploration, local development
- **Created by**: `python -m venv .venv` (manual, optional)
- **Contains**: Development dependencies for IDE/testing
- **Marker file**: `.venv/.THIS_IS_DEV_VENV`
- **Env vars**: `VENV_PURPOSE=dev`, `VENV_TYPE=development`
- **Usage**: Activate for manual work: `source .venv/bin/activate`
- **Python**: Can use `python` or `python3` when activated

#### Protection Mechanisms (8 Layers)
1. **Marker files** - Identify venv purpose
2. **Environment variables** - Set on activation
3. **Runtime checks** - Every CI script validates venv
4. **CI runner enforcement** - ci/ci uses explicit path
5. **Bootstrap separation** - Only creates ci/.venv
6. **Documentation** - This section and shebangs
7. **Shared library** - ci/ci_lib.py with `enforce_venv_ci()`
8. **Gitignore** - Both venvs ignored

#### For AI Assistants / LLMs - CRITICAL RULES

**When writing CI scripts:**
- ✅ ALWAYS use: `from ci_lib import enforce_venv_ci` at top
- ✅ ALWAYS call: `enforce_venv_ci(__name__)` immediately
- ✅ ALWAYS run via: `./ci/ci <action>`
- ❌ NEVER use: `#!/usr/bin/env python3` without checks
- ❌ NEVER use: `python` or `python3` commands
- ❌ NEVER use: `.venv` for CI

**When writing development code:**
- ✅ Use `.venv/bin/python` or activate `.venv`
- ✅ For manual testing and exploration only
- ❌ NEVER use `ci/.venv` for development
- ❌ NEVER install dev dependencies in `ci/.venv`

**How to check which venv:**
```bash
# Before running any command, verify:
echo $VIRTUAL_ENV           # Should show ci/.venv or .venv
echo $VENV_PURPOSE          # Should show 'ci' or 'dev'
python -c "import sys; print(sys.prefix)"  # Check Python location
```

## Universal Policies

### Temporary Files
Use `./.tmp/` only (not `/tmp`, `~/tmp`, `/var/tmp`)

### TODO
`TODO.md` is single source of truth (lightweight Markdown, updated directly by LLM)

### CI Environment
Always use `ci/.venv` for CI/tooling. Bootstrap creates/populates it. CI scripts run bootstrap first.

### Character Policy

**MUST follow `CHARS-POLICY.md`**:
1. Only approved emojis/ASCII
2. No other Unicode symbols
3. **Logs**: strict ASCII-only (no emojis)

Absolute rule, no exceptions.

### Git Branches

Format: `<type>/<issue-ref>/<short-description>`

**Types**: feat, fix, chore, docs, test, refactor, hotfix, release
**Issue**: Ticket ID or `no-ref`
**Examples**: `feat/PROJ-123/add-oauth`, `fix/no-ref/memory-leak`
**Enforced**: `ci/ci.d/10-branch-name.py`

## Hyperlib-Specific Context

### Relationship to Forge-Python Template (CRITICAL)

**Hyperlib is a forge-deployed forge-python package project.**

This means:
- Hyperlib was originally generated using forge-python template
- It follows the same structure as any forge-generated Python package
- **AI assistants MUST manually apply general changes from forge-python to hyperlib**
- When forge-python template CI/bootstrap/structure changes, apply them here too
- Hyperlib serves as a real-world validation of the forge-python template

**Example workflow:**
1. Change is made to forge-python template (e.g., new CI script, updated bootstrap)
2. AI assistant must manually apply equivalent change to hyperlib
3. Test in hyperlib to validate the change works in a real project
4. If issues found, fix in both forge-python template and hyperlib

**DO NOT:**
- Assume changes to forge-python automatically apply to hyperlib
- Treat hyperlib as independent from forge-python template
- Skip applying forge-python improvements to hyperlib

**Why this matters:**
- Hyperlib validates that forge-python template changes work in real projects
- Keeps hyperlib up-to-date with latest forge standards
- Ensures consistency across all forge-generated projects

### Self-Contained Requirement

**CRITICAL**: Hyperlib MUST be completely self-contained with NO external file references.

- All code must work standalone
- No imports from parent directories
- No references to forge or other projects
- Bootstrap installs hyperlib from JFrog (published version)

### Bootstrap Paradox Resolution

Hyperlib's bootstrap.py installs hyperlib from JFrog, not from local source. This ensures:
1. Bootstrap works with minimal dependencies
2. Testing uses published package (real-world validation)
3. No circular dependencies
4. Consistent with all other projects

### Development Workflow

1. Make changes to `src/hyperlib/`
2. Commit with conventional commit messages (feat:, fix:, etc.)
3. Run: `FORCE_RELEASE=1 ./ci/ci publish`
   - Semantic-release auto-versions based on commits
   - Creates/updates CHANGELOG.md
   - Tags and pushes to GitHub
   - GitHub Actions builds and publishes to JFrog Artifactory

### Version Management

- Semantic versioning via conventional commits
- Git tags are source of truth
- VERSION file auto-synced by semantic-release
- pyproject.toml and `__version__` auto-updated

Current version: **1.5.5**

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

## Testing

```bash
# Unit tests
pytest tests/

# Integration test (bootstrap from published package)
rm -rf ci/.venv && ./ci/bootstrap --install
```

## CI Commands

```bash
./ci/ci [action] [flags]

Actions:
  check     - Run all CI checks (lint, test, type-check)
  build     - Build wheel and sdist locally (for testing)
  release   - Full semantic-release workflow (version, tag, build)
  publish   - Release + push to GitHub (triggers GitHub Actions to publish to JFrog)
  clean     - Remove build artifacts

Flags:
  --push    - Push changes to remote after release (opt-in)
  --force   - Force action without checks
```

**Common workflows:**
```bash
./ci/ci check                    # Pre-commit checks
./ci/ci build                    # Build package locally (for testing)
FORCE_RELEASE=1 ./ci/ci publish  # Full release: version → tag → push → GitHub Actions publishes
```

**Publishing to JFrog:**

Two publishing methods are available:

1. **GitHub Actions (Production)** - Triggered by version tags
   - Workflow: `.github/workflows/jfrog-publish.yml`
   - Uses GitHub Secrets: `ARTIFACTORY_USERNAME`, `ARTIFACTORY_PASSWORD`
   - Automatic on version tag push

2. **Local Publishing (Development/Testing)** - Direct upload via twine
   ```bash
   # Publish with auto-detect (uses creds from .env)
   ./ci/run --script 80-build.py publish

   # Force publish even without auto-detect
   JFROG_PUBLISH=true ./ci/run --script 80-build.py publish

   # Skip publishing
   JFROG_PUBLISH=false ./ci/run --script 80-build.py publish
   ./ci/run --script 80-build.py publish --no-publish
   ```

**JFrog Authentication Methods:**

Supports both token and username/password authentication:

1. **Token Auth (Preferred)**:
   ```bash
   JF_TOKEN=your-access-token
   JF_TOKEN_USER=artifactory@hypersec.io  # Optional, default shown
   ```

2. **Username/Password (Fallback)**:
   ```bash
   JF_USER=your-username
   JF_PASSWORD=your-password
   ```

**JFROG_PUBLISH Environment Variable:**

Controls local JFrog publishing behavior:

- `JFROG_PUBLISH=false` - Never publish (skip)
- `JFROG_PUBLISH=true` - Always publish (requires credentials)
- `JFROG_PUBLISH` unset - Auto-detect from credentials (default)

**Credential Sources:**
- `.env` file → Local development (bootstrap + publishing)
- GitHub Secrets → Production publishing via GitHub Actions

## Role in Forge Ecosystem

Hyperlib serves two roles:

1. **Production library**: Shared utilities for all HyperSec Python projects
2. **Template test case**: Real-world validation of forge-python package template

All changes to hyperlib that affect template structure should be documented in `docs/TEMPLATE-CHANGES.md` for backporting to forge-python.

## Documentation

- **STATE.md** (this file) - Project state and instructions
- **README.md** - User-facing documentation
- **docs/ARTIFACTORY.md** - JFrog setup and publishing
- **docs/BOOTSTRAP-ANALYSIS.md** - Bootstrap implementation details
- **docs/TEMPLATE-CHANGES.md** - Template change tracking
- **TODO.md** - Task list
- **CHANGELOG.md** - Version history