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

**Setup**: `./scripts/bootstrap --install` | **Check**: `./scripts/bootstrap`

**3 Phases**:
1. System Python creates `.venv-ci`
2. Installs `hyperlib` from JFrog Artifactory
3. Imports hyperlib, runs `bootstrap.d/*` scripts

**Requires**: `.env` with `JF_USER`/`JF_PASSWORD`, Python 3.11+, JFrog network access

**Installs**: `.venv-ci`, hyperlib (latest from JFrog), nox, pytest, ruff, black, mypy, twine, semantic-release

### Virtual Environment (CRITICAL)

- `.venv` - Development (IDE, manual testing)
- `.venv-ci` - CI/automation (nox, pytest, tools)

**NEVER mix them**. Check before commands: `pwd`, `echo $VIRTUAL_ENV`

## Universal Policies

### Temporary Files
Use `./.tmp/` only (not `/tmp`, `~/tmp`, `/var/tmp`)

### TODO
`TODO.md` is single source of truth (lightweight Markdown, updated directly by LLM)

### CI Environment
Always use `.venv-ci` for CI/tooling. Bootstrap creates/populates it. CI scripts run bootstrap first.

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
**Enforced**: `scripts/ci.d/10-branch-name.py`

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
3. Run: `FORCE_RELEASE=1 ./scripts/ci publish`
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
rm -rf .venv-ci && ./scripts/bootstrap --install
```

## CI Commands

```bash
./scripts/ci [action] [flags]

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
./scripts/ci check                    # Pre-commit checks
./scripts/ci build                    # Build package locally (for testing)
FORCE_RELEASE=1 ./scripts/ci publish  # Full release: version → tag → push → GitHub Actions publishes
```

**Publishing to JFrog:**
- Publishing happens ONLY via GitHub Actions (triggered by version tags)
- GitHub Secrets required: `ARTIFACTORY_USERNAME`, `ARTIFACTORY_PASSWORD`
- Workflow: `.github/workflows/jfrog-publish.yml`

**Note on credentials:**
- `JF_USER`/`JF_PASSWORD` in `.env` → Bootstrap only (installing hyperlib during development)
- GitHub Secrets → Production publishing to JFrog Artifactory

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