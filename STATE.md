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

### Pip Install from JFrog ONLY (CRITICAL)

**BEST SOLUTION: Use `uv` with `tool.uv.sources` configuration:**

```bash
uv pip install <package>
```

With pyproject.toml:
```toml
[[tool.uv.index]]
name = "jfrog"
url = "https://your-jfrog-url/simple"
explicit = true

[tool.uv.sources]
package-name = { index = "jfrog" }
```

This forces the package to ONLY come from JFrog with no fallback to public PyPI.

**ALTERNATIVE (if not using uv): Use `--no-index` with `--find-links`:**

```bash
pip install <package> --no-index --find-links <jfrog_url>
```

**Why each approach:**
- `uv pip install` - Respects `tool.uv.sources` in pyproject.toml (cleanest solution)
- `--no-index` - Prevents pip from using any default indexes (including PyPI)
- `--find-links` - Specifies the ONLY source to check

**CRITICAL for Nuitka:**
- **hypersec-pypi-LOCAL repository ONLY has Nuitka Commercial 2.7.16 (Commercial: 3.8.5)**
- Confirmed by manual download: `Nuitka/2.7.16/nuitka-2.7.16-cp311-cp311-linux_x86_64.whl` is Commercial
- **AI AGENTS: JFrog LOCAL repo is ALWAYS Commercial - NEVER assume it has OSS!**
- Artifactory MAY cache public PyPI packages, but hypersec-pypi-LOCAL is curated and contains ONLY Commercial
- Install with version pinning: `pip install nuitka==2.7.16` forces JFrog version (public PyPI has 2.8.1)

**IMPORTANT: Do NOT use `--no-index` with `--index-url`!**
- `--no-index` tells pip to ignore ALL indexes, including the one specified in `--index-url`
- This is documented pip behavior and will cause "no matching distribution" errors

**WRONG (will check multiple indexes):**
```bash
pip install <package> --index-url <jfrog_url>  # WRONG - still checks pip.conf and env vars
```

**ALSO WRONG (incompatible flags):**
```bash
pip install <package> --no-index --index-url <jfrog_url>  # WRONG - --no-index overrides --index-url
```

**This is critical for packages like Nuitka where JFrog should have Commercial but public PyPI has OSS.**

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

### Nuitka Build Profile (Code Protection)

Hyperlib supports **Nuitka Commercial** compilation for creating standalone executables with code protection. This is controlled via environment variables and integrates seamlessly with the existing CI system.

**Build Profiles:**

- `BUILD_PROFILE=package` (default): Standard Python wheel/sdist
- `BUILD_PROFILE=nuitka`: Nuitka-compiled standalone executable

**Protection Levels (NUITKA_PROTECTION):**

- `none`: Basic compilation only
- `minimal`: Standalone mode only
- `data-hiding`: Encrypt string constants and names
- `traceback`: Encrypt stdout/stderr and tracebacks
- `recommended` (default): Full protection stack (data-hiding + traceback + isolated)

**Requirements:**

1. C compiler (gcc/clang for Linux/macOS, MSVC/MinGW for Windows)
2. Nuitka Commercial from HyperSec private PyPI
3. JFrog credentials in `.env`

**Bootstrap automatically checks:**
- C compiler availability (provides installation hints if missing)
- Nuitka Commercial installation (installs from HyperSec PyPI if needed)

**Nuitka Build Commands:**

```bash
# Build with default protection (recommended)
BUILD_PROFILE=nuitka ./ci/ci build

# Build with specific protection level
BUILD_PROFILE=nuitka NUITKA_PROTECTION=data-hiding ./ci/ci build

# Build with no protection (fastest)
BUILD_PROFILE=nuitka NUITKA_PROTECTION=none ./ci/ci build
```

**Output:**
- Standard build: `dist/*.whl` and `dist/*.tar.gz`
- Nuitka build: `dist-nuitka/*.bin` (or `.exe` on Windows)

**Key Management (Traceback Encryption):**

When using `traceback` or `recommended` protection, encryption keys are automatically generated:

- Keys stored in: `.keys/hyperlib-<version>-<timestamp>.key`
- Keys are gitignored (NEVER commit!)
- Keys required to decrypt logs/tracebacks from compiled binaries
- Backup keys securely (password manager, key vault)

**Security Warning:**

When traceback encryption is enabled, the build prints a prominent security banner with key location and backup instructions. **CRITICAL**: These keys are required to decrypt logs!

**Testing Nuitka Build:**

```bash
# Build Nuitka executable locally
BUILD_PROFILE=nuitka ./ci/ci build
```

**See also:** [ci/docs/NUITKA.md](ci/docs/NUITKA.md) for detailed Nuitka usage guide

### Publishing to JFrog

**Publishing is handled EXCLUSIVELY by GitHub Actions**

Local CI builds artifacts to `dist/`, GitHub Actions publishes them to JFrog Artifactory.

**Workflow:**

1. **Local**: Build and create version tag
   ```bash
   ./ci/ci build                    # Build to dist/
   FORCE_RELEASE=1 ./ci/ci publish  # Create version, tag, push
   ```

2. **GitHub Actions**: Automatically triggered by version tag push
   - Workflow: `.github/workflows/jfrog-publish.yml`
   - Builds package fresh from source
   - Publishes to JFrog using GitHub Secrets
   - Uses: `ARTIFACTORY_USERNAME`, `ARTIFACTORY_PASSWORD`

**Why GitHub Actions Only?**

- **Single Source of Truth**: Only one place publishes
- **Security**: JFrog credentials only in GitHub Secrets
- **Auditability**: All publishes tracked in GitHub Actions logs
- **Consistency**: Same build process for everyone

**JFrog Authentication (Bootstrap Only):**

JFrog credentials in `.env` are used ONLY for bootstrap (installing dependencies):

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