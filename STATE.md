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
- **Version**: 1.0.1 (see VERSION file)

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
2. Bump version in `VERSION`, `pyproject.toml`, `src/hyperlib/__init__.py`
3. Build: `python -m build`
4. Publish to JFrog: `python -m twine upload --repository-url ... dist/*`
5. Test with `rm -rf .venv-ci && ./scripts/bootstrap --install`

### Version Management

- Git tags are source of truth
- VERSION file synced from tags
- pyproject.toml version must match
- `__version__` in `__init__.py` must match

Current version: **1.0.1**

## Module Structure

```
hyperlib/
├── __init__.py       # Exports: config, logger, timeout, container, bootstrap
├── bootstrap.py      # load_dotenv, list_sorted_scripts, load_defaults_yaml, ensure_dependency
├── config.py         # get_logging_config, cascading config
├── logger.py         # get_logger, setup, RFC 3339 timestamps
├── timeout.py        # Async timeout utilities
├── container.py      # Dependency injection
├── cache.py          # Caching utilities
├── core.py           # Core functionality
├── resources.py      # Resource management
├── sampling.py       # Data sampling
└── exceptions.py     # Custom exceptions
```

## Testing

```bash
# Unit tests
pytest tests/

# Integration test (bootstrap from published package)
rm -rf .venv-ci && ./scripts/bootstrap --install
```

## Publishing to JFrog

```bash
# Build
python -m build

# Upload
python -m twine upload \
  --repository-url https://hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local \
  -u "$JF_USER" -p "$JF_PASSWORD" \
  dist/*
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