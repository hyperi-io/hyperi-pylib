# Hyperlib - Project State

**Repository**: https://github.com/hypersec-io/hyperlib
**Type**: Python package (shared library)
**Purpose**: Enterprise infrastructure for all HyperSec Python projects

## Session 2025-11-07 Continued (Part 2)

### ClickHouse Database Support - Complete ✅
- Added ClickHouse to `build_database_url()` in hyperlib.database
  - Default port: 9000 (native protocol)
  - Scheme: `clickhouse://`
  - Follows same pattern as PostgreSQL, MySQL, Redis
- Comprehensive tests: 11 tests (7 ClickHouse + 4 regression)
- All tests passing, backward compatible

### Sensitive Data Masking - Tier 1 Complete ✅
- Implemented automatic sensitive data filter for logs
  - 30+ sensitive field patterns (passwords, tokens, API keys, secrets)
  - Multiple format support: JSON, form data, database URLs, key=value
  - Bearer token detection, database URL password masking
  - Custom field support (class-level and instance-level)
- Integrated with hyperlib logger (automatic, zero-config)
  - Default: ENABLED (masks by default)
  - Configurable: `HYPERLIB_LOGGING__MASK_SENSITIVE_DATA=false`
  - Performance: ~5-10μs per log message (negligible overhead)
- Comprehensive tests: 22/22 passing
- Zero external dependencies (stdlib `re` only)

### Opinionated Anonymizer with Presidio - Complete ✅
- Implemented comprehensive anonymizer package (`hyperlib.anonymizer`)
  - **Presets:** minimal (secrets), standard (default), compliance (HIPAA/GDPR/PCI-DSS)
  - **Strategies:** REPLACE, REDACT, MASK, HASH, ENCRYPT
  - **Presidio integration:** ML-based PII detection (50+ entity types)
  - **Graceful fallback:** Helpful errors if Presidio not installed
- **StreamingAnonymizer** for efficient large-data processing:
  - LRU caching for consistent anonymization
  - Optimized for: ClickHouse queries, Polars DataFrames, Kafka streams, large files
  - DataFrame support: Polars (lazy + eager), Pandas
  - Memory-efficient iterators (millions of rows, GB+ files)
- **Convenience functions:**
  - `anonymize_text()`, `anonymize_dict()`, `scan_for_pii()`
  - `anonymize_config_file()`, `scan_file_for_secrets()` (pre-commit hooks)
- **Installation:** `pip install hyperlib[presidio]` (optional dependency)
- **Use cases:**
  - Large database result sets (millions of rows)
  - Data processing (Polars lazy evaluation)
  - Message queues (Kafka, RabbitMQ)
  - Large files (GB+ logs, JSONL)
  - Config file PII detection

### HyperCI Secret Scanning Strategy - Design Complete ✅
- **Researched & selected tool: Gitleaks** (best for CI/CD pre-commit in 2025)
  - Fast (Golang), simple config, low false positives
  - Beats TruffleHog (too slow), detect-secrets (complex), Presidio (wrong domain)
  - Industry standard for pre-commit secret scanning
- **Multi-layer defense strategy:**
  1. Pre-commit hook (local, immediate feedback)
  2. Pre-receive hook (server, cannot bypass)
  3. CI/CD pipeline (PR checks, auditable)
  4. Periodic full scans (historical leaks)
- **Clear separation:**
  - **Gitleaks:** Pre-commit secret scanning (hyperci)
  - **Presidio:** Runtime PII anonymization (hyperlib)
  - Different tools, different domains
- **Design document:** `.tmp/hyperci-secret-scanning-design.md`
  - Complete implementation guide
  - Code examples, configuration, testing
  - Estimated implementation: 3-4 hours

### Next Phase (Future Sessions)
- Integrate Presidio with logger filters (two-tier approach)
  - Tier 1 (default): Regex-based (fast, zero deps) ✅ Already done
  - Tier 2 (opt-in): Presidio (`hyperlib[presidio]`, better accuracy)
  - Graceful fallback if Presidio not installed
- Add comprehensive tests for anonymizer package
- Optional: Implement Gitleaks integration in hyperci

### Python Standards Documentation - Complete (Earlier Session)
- Added comprehensive "No Mocks or Mock Code Policy" to PYTHON-STANDARDS.md
  - Policy: Production code must be complete, no placeholders/TODOs
  - Examples: Bad (mock) vs Good (real) implementations
  - AI assistant warning signs and enforcement checklist
  - Migration path for existing mock code
- Added "Hyperlib Infrastructure Standards" to PYTHON-STANDARDS.md
  - Concise "What to Use When" reference table
  - Module standards for logging, config, runtime, database, metrics, CLI
  - Quick start examples (Application framework vs individual components)
  - Replaced verbose documentation with "use this for that" approach
- Separated hyperci-specific guidance from general project standards
  - Moved ci_lib logging instructions to STATE.md (hyperci development only)
  - PYTHON-STANDARDS.md now covers all projects using hyperlib
  - Clear distinction: ci_lib (internal) vs hyperlib (standard)

## Session 2025-11-03 Completed

### VERSION Sync & Environment Variable Standardization - Complete
- Fixed VERSION file sync (plain `2.6.2` format, atomic with git tag)
- Standardized ALL env vars to CI_ prefix (8 orphans removed)
- Removed 647 lines of complexity (version sync + redundant publish)
- Added nuitka-only release mode (--nuitka-only flag)
- Released v2.6.1 and v2.6.2 successfully

### Code & Documentation Cleanup - Complete
- Separated build/publish responsibilities (removed 99 duplicate lines)
- Updated all documentation to match code
- Fixed README.md API examples
- Moved write-version.py to CI infrastructure
- Removed .python-version (uv uses pyproject.toml)
- Cleaned up 3 obsolete file references

## Session 2025-10-31 Completed

### ONE .venv Migration - Complete
- Unified .venv at project root (runtime + CI tools)
- Published v2.4.4 to JFrog (standard + Nuitka x64 + ARM64)

### Nuitka Builds - Complete
- Package mode: .whl with .so files (NO .py source)
- App mode: Binary + tarball distribution
- Multi-arch: x64 + ARM64

### uv-Managed Python - Complete
- No system Python dependency
- uv downloads Python automatically
- Works on any OS

### Test Status
- HyperCI unit: 56/56 (100%)
- HyperCI integration: 64/64 (100%), 4 skipped
- Hyperlib unit: 143/143 (100%)
  - Database tests: 11/11 (ClickHouse + regression)
  - Logger filter tests: 22/22 (sensitive data masking)

## Quick Start

```bash
# Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup
./ci/bootstrap --install

# Test
./ci/run check

# Build
./ci/run build

# Nuitka
./ci/run build --nuitka
```

## Strategic Goal: Replace ci_lib with Hyperlib

**Long-term architecture goal** (when hyperlib is stable):

Replace ci_lib.py functions with hyperlib equivalents to reduce duplication:
- Configuration: ci_lib.get_config_value() → hyperlib.config.get_config()
- Logging: ci_lib logger → hyperlib.logger
- Utilities: Port shared functions to hyperlib

**Current Blocker:**
- Circular dependency risk (hyperlib needs hyperci for CI, hyperci needs hyperlib for utils)
- hyperlib must be stable first

**Strategy:**
1. Stabilize hyperlib (production-ready, well-tested)
2. Port ci_lib functions to hyperlib gradually
3. Update hyperci to import from hyperlib
4. Remove duplicate code from ci_lib.py
5. ci_lib becomes thin wrapper around hyperlib

**When Ready:**
- hyperlib config.py has full 7-layer cascade (DONE - Session 2025-11-04)
- hyperlib.config.get_config() supports additional files (DONE - Session 2025-11-04)
- hyperlib logger.py is production-ready (DONE)
- hyperci pip installs hyperlib from JFrog (published package)
- hyperci imports from hyperlib: `from hyperlib.config import get_config`
- ci_lib becomes thin wrapper (80% reduction possible)

## HyperCI Development Guidelines

### Logging in CI Scripts (hyperci development only)

**When developing CI scripts for hyperci, use ci_lib logger:**
```python
from ci_lib import logger

logger.info("Starting build...")
logger.warning("Tests skipped")
logger.error("Build failed")
```

**Features:**
- Consistent formatting across all CI scripts
- Color output for terminal readability
- Appropriate severity levels (info, warning, error)

**Note:** This is ONLY for hyperci CI script development. Normal projects should use hyperlib.logger instead.

## Next Tasks
- Clean up ci_lib.py naming (get_ prefix inconsistency)
- Test coverage for configuration cascade
- Documentation alignment


---

<!-- HYPERCI_STATE_MD: HYPERCI_STATE_MD: ci/modules/common/templates/STATE.md -->
# HyperCI - Common CI/CD Documentation

**Auto-appended to project STATE.md during AI setup**

## Critical Policies for AI Assistants

**ALWAYS READ ON SESSION START:**
1. This STATE.md file (you're reading it now)
2. `TODO.md` (current tasks and priorities)
3. `ci-local/CODE-ASSISTANT.md` - AI assistant guidance (REQUIRED)
4. **ALL files in `ci/docs/standards/`** (critical standards and policies)
   - `GIT-WORKFLOW.md` - Git conventions (REQUIRED)
   - `CHARS-POLICY.md` - Character restrictions
   - Any other standards files present

**Do not skip reading the standards files. They contain critical project-specific requirements.**

### 1. Commit Message Type Selection (UNDERSTATE, NOT OVERSTATE)

**AI assistants frequently overstate importance. Always err on understatement.**

**Default to `fix:` when uncertain:**
- ✅ `fix:` is almost always correct for bug fixes, improvements, refactors
- ❌ Don't use `feat:` unless it's truly a **NEW VERY SIGNIFICANT and BROAD** feature
- ❌ Don't use `BREAKING CHANGE:` unless it breaks backward compatibility

**Valid commit types:**
- `feat:` - **NEW VERY SIGNIFICANT and BROAD user-facing feature** (minor version bump) - RARELY USE
- `fix:` - **Bug fix, improvement, refactor, cleanup** (patch bump) - DEFAULT CHOICE
- `perf:` - Performance optimization only (patch bump)
- `chore:` - Maintenance, deps, config (no bump)
- `docs:` - Documentation only (no bump)
- `test:` - Tests only (no bump)
- `ci:` - CI configuration (no bump)

**Format:** `<type>: <description>` or `<type>(<scope>): <description>`

**Examples of correct usage:**
```
fix: update CI structure documentation          # NOT feat: (just docs)
fix: add commit message validation              # NOT feat: (internal tool)
fix: improve test coverage                      # NOT feat: (tests)
chore: update ci submodule                      # NOT feat: or fix:
feat: add OAuth authentication for users        # OK - NEW user feature
```

**Why this matters:**
- Semantic versioning depends on correct types
- Over-using `feat:` causes unnecessary minor version bumps
- Projects accumulate false "features" in changelogs
- `fix:` is safer and more accurate for most changes

**Validation:** commit-msg hook enforces format (auto-installed by bootstrap)

### 2. Directory Structure

**Read-only ci/ (git submodule):**
- `ci/` - HyperCI scripts (NEVER modify directly)
- `ci/modules/` - Modular CI scripts organized by language
- `ci/docs/` - Documentation

**Writable ci-local/ (project-specific):**
- `ci-local/.venv/` - CI tools only (pytest, ruff, etc.)
- `ci-local/.env` - Credentials (gitignored)
- `ci-local/pyproject.toml` - CI tool dependencies

**Project workspace:**
- `.venv/` - Project dependencies (development)
- `.tmp/` - Temporary files (ALWAYS use this, not /tmp)

### 3. Virtual Environments

**Two separate venvs - NEVER mix:**
- `ci-local/.venv` - CI tools (for CI scripts ONLY)
- `.venv` - Project dependencies (for development)

**CI scripts must use ci-local/.venv:**
```python
if "ci-local/.venv" not in sys.prefix:
    sys.exit("ERROR: Must run in ci-local/.venv")
```

### 4. Bootstrap & Workflow

**Bootstrap (first-time setup):**
```bash
./ci/bootstrap --install
```

Creates both venvs, installs dependencies, installs git hooks.

**Run CI checks:**
```bash
./ci/run check       # All checks (tests, lint, type-check)
./ci/run test        # Tests only
./ci/run build       # Build package
```

**Git hooks (auto-installed by bootstrap):**
- `commit-msg` - Validates branch name, message format, removes AI attribution
- Blocks commits if invalid, warns about formatting issues

### 5. CI Script Locations

**New modular structure:**
```
ci/modules/
├── common/
│   ├── bootstrap.d/     # Bootstrap scripts (run during setup)
│   ├── run.d/           # Runtime checks (branch name, etc.)
│   ├── gitci.d/         # Git operations (hooks, etc.)
│   └── templates/       # File templates (.gitignore, etc.)
└── python/
    ├── bootstrap.d/     # Python bootstrap scripts
    └── run.d/           # Python CI checks (test, build, etc.)
```

**Execution:** All CI scripts run via bash wrappers using `.d` pattern
- `ci/bootstrap` orchestrates `bootstrap.d/*.py` scripts
- `ci/run` orchestrates `run.d/*.py` scripts
- `ci/gitci` orchestrates `gitci.d/*.py` scripts

### 6. TODO Management

**Use TODO.md ONLY:**
- Add todos to `TODO.md` (project root)
- NEVER use `# TODO:` in code comments
- NEVER put TODOs in commit messages

### 7. Temporary Files

**Always use `./.tmp/`:**
- Use `./.tmp/` (project root, gitignored)
- NOT `/tmp`, `~/tmp`, or `/var/tmp`

### 8. Bash Command Execution

**See `ci-local/CODE-ASSISTANT.md` for complete bash usage guidance to minimize permission prompts.**

Quick summary:
- Avoid: `&&`, `||`, `;`, `|` (triggers permission prompts)
- Use: Separate Bash calls, `.tmp/` intermediate files, output redirection (`>`)

## Configuration Cascade

**Environment variables > .env > ci.yaml > defaults.yaml**

**Common env vars:**
- `CI_SKIP_HOOKS=true` - Skip git hook installation
- `CI=true` - Running in CI environment
- `BOOTSTRAP_INSTALL=1` - Enable bootstrap installation

## Quick Reference

**Update ci/ submodule:**
```bash
cd ci && git pull origin main && cd ..
git add ci && git commit -m "chore: update ci submodule"
```

**Contribute to HyperCI:**
1. Work in `ci/` directory (changes tracked in hyperci repo)
2. Commit to `hypersec-io/hyperci` repository
3. Update project's ci/ submodule reference

**Troubleshooting:**
- Bootstrap fails: Check `ci-local/.env` has credentials
- Wrong venv: CI scripts enforce ci-local/.venv (will error)
- Submodule issues: `git submodule update --init --force`

---

**See also:**
- `ci-local/CODE-ASSISTANT.md` - AI assistant guidance (common + language-specific)
- `ci/docs/README.md` - Complete documentation
- `ci/docs/standards/GIT-WORKFLOW.md` - Git conventions


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
./ci/run build --nuitka  # Nuitka compiled binary
```

**Releasing:**
```bash
./ci/run release --dry-run   # Preview next version
./ci/run release             # Create release + push tag (default)
./ci/run release --no-push   # Create release locally (don't push)
```

**Publishing:**
```bash
./ci/run publish         # Build + publish to JFrog (manual, discouraged)
./ci/run verify-publish  # Verify package exists in JFrog
```

### Python-Specific Environment Variables

**Build Control:**
- `CI_NUITKA=1` - Enable Nuitka build (set by --nuitka flag)
- `CI_NUITKA_ONLY=1` - Publish only Nuitka wheels, skip standard (set by --nuitka-only)

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
- Use `./ci/run release` (push is default)
- Use `--no-push` flag to keep local (sets CI_NO_PUSH=1)
- Use `--force` flag to bypass checks (sets CI_FORCE=1)

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
