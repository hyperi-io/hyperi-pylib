# Hyperlib - Project State

## CRITICAL: Read Documentation First

<!--
AI AGENTS: Read these files BEFORE starting work:
1. STATE.md (or CLAUDE.md symlink)
2. HyperCI section below - ci/ is git subtree from hypersec-io/hyperci
3. ci/docs/SUBTREE-USAGE.md - How to use hyperci subtree
4. docs/CHARS-POLICY.md - Character restrictions (ASCII logs, limited emoji)
5. docs/CONTRIBUTING.md - Workflow and conventions
6. README.md - Project overview
7. docs/ARTIFACTORY.md - JFrog publishing
-->

## Project Overview

**Hyperlib** is a shared Python library providing enterprise infrastructure for all HyperSec Python projects.

- **Type**: Python package (publishable library)
- **Purpose**: Shared utilities (logging, config, bootstrap, caching, containers, timeouts)
- **Package name**: `hyperlib`
- **Repository**: `https://github.com/hypersec-io/hyperlib`
- **Published to**: JFrog Artifactory private PyPI
- **Version**: 1.5.0 (see VERSION file)

## HyperCI - Centralized CI Infrastructure

**CRITICAL**: Hyperlib uses [HyperCI](https://github.com/hypersec-io/hyperci) via **git subtree**.

### Architecture

The `ci/` directory is a git subtree from `hypersec-io/hyperci`:
- **Central Repo**: https://github.com/hypersec-io/hyperci
- **Method**: Git subtree (embedded in project)
- **Updates**: `git subtree pull --prefix ci https://github.com/hypersec-io/hyperci.git main --squash`
- **Customization**: `ci/ci.yaml` (project-specific, protected from updates)

### What This Means

**CI Scripts are Centralized:**
- ✅ All `ci/` scripts come from hyperci repo
- ✅ Bootstrap, build, test, Nuitka scripts shared across ALL projects
- ✅ Updates to hyperci automatically available to all projects
- ✅ One fix in hyperci → all projects benefit

**Configuration is Project-Specific:**
- ✅ Each project has its own `ci/ci.yaml`
- ✅ Protected from subtree updates (`.gitattributes: ci/ci.yaml merge=ours`)
- ✅ Hyperlib's `ci/ci.yaml` stays under version control in this repo

### Updating HyperCI

```bash
# Pull latest from hyperci (updates all scripts, keeps ci/ci.yaml intact)
git subtree pull --prefix ci https://github.com/hypersec-io/hyperci.git main --squash

# Test after update
./ci/bootstrap --install
ci/.venv/bin/python ci/python/ci.d/20-python-test.py check
```

### Contributing Back to HyperCI

```bash
# If you improve a script in hyperlib's ci/
git subtree push --prefix ci https://github.com/hypersec-io/hyperci.git fix/my-improvement

# Create PR in hyperci repo
# Once merged, all projects can pull the improvement
```

**See Also**: [ci/docs/SUBTREE-USAGE.md](ci/docs/SUBTREE-USAGE.md) for complete guide

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
3. Create release tag and push to GitHub:
   ```bash
   FORCE_RELEASE=1 ./ci/ci publish  # Creates tag, pushes to GitHub
   ```
   - Semantic-release auto-versions based on commits
   - Creates/updates CHANGELOG.md
   - Tags and pushes to GitHub
   - **GitHub Actions automatically builds and publishes to JFrog** (no manual publish!)

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

**Dual-Build Strategy: Local vs GitHub Actions**

Hyperlib uses a two-stage Nuitka build approach:

1. **Local Build** (Fast Testing):
   - Purpose: Quick validation that Nuitka compilation works
   - Architecture: **Local CPU only** (x64 or ARM64, whichever you're on)
   - Trigger: `BUILD_PROFILE=nuitka ./ci/ci build`
   - Output: `dist-nuitka/hyperlib-linux-{arch}.bin` (or `.exe` on Windows)
   - Cost: Free (local machine)
   - Use: Test Nuitka before expensive GitHub Actions run

2. **GitHub Actions Build** (Multi-Architecture):
   - Purpose: Production builds for all supported architectures
   - Architectures: **x64 AND ARM64** (configurable in `ci/ci.yaml`)
   - Trigger: Automatic on version tags (`v*`) or manual workflow_dispatch
   - Output: Compiled wheels (`.whl` with `.so` files) for each architecture
   - Publishing: Uploads to JFrog Artifactory PyPI repository
   - Cost: ~$0.056-0.168 per build (depending on enabled platforms)
   - Use: Production releases with multi-arch support

**Why Two Build Modes?**

- **Speed**: Local builds complete in 5-10 minutes on your machine
- **Cost**: GitHub Actions ARM64 builds cost 2x Linux x64, macOS costs 20x
- **Safety**: Test locally before triggering expensive cloud builds
- **Flexibility**: Local builds for development, cloud builds for distribution

**Third-Party Runner Configuration:**

Hyperlib uses cost-optimized third-party runners for significant savings:

```yaml
# ci/ci.yaml
nuitka:
  # BuildJet for ALL Linux builds (50% cheaper)
  buildjet:
    enabled: true  # Default: true - use BuildJet for x64 AND ARM64

  # Cirrus Runners for macOS builds (95% cheaper)
  cirrus:
    enabled: true  # Default: true - use Cirrus for macOS
```

**BuildJet** (Linux x64 + ARM64):
- **When enabled**: Both x64 and ARM64 use BuildJet runners ($0.004/min each)
- **When disabled**: Falls back to GitHub ($0.008/min x64, ARM64 unavailable for private)
- **Cost savings**: 50% cheaper for x64, enables ARM64 for private repos

**Cirrus Runners** (macOS):
- **When enabled**: Uses M4 Pro runners ($0.015/min effective)
- **When disabled**: Falls back to GitHub macOS ($0.16/min - 10x more!)
- **Cost savings**: 95% cheaper than GitHub
- **Setup required**: https://cirrus-runners.app/setup/

**Nuitka Build Commands:**

```bash
# Local build (tests on your architecture only)
BUILD_PROFILE=nuitka ./ci/ci build

# With specific protection level
BUILD_PROFILE=nuitka NUITKA_PROTECTION=data-hiding ./ci/ci build

# Fast build (no protection, for testing)
BUILD_PROFILE=nuitka NUITKA_PROTECTION=none ./ci/ci build

# GitHub Actions multi-arch build (automatic on tag push)
FORCE_RELEASE=1 ./ci/ci publish  # Creates tag, triggers GitHub Actions
```

**Output:**

- **Local build**: `dist-nuitka/*.bin` (or `.exe` on Windows) - single architecture
- **GitHub Actions**: `dist/*.whl` - compiled wheels for x64 and ARM64 (if enabled)
- **Standard build**: `dist/*.whl` and `dist/*.tar.gz` - pure Python (no Nuitka)

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

**⚠️ CRITICAL: Publishing is handled EXCLUSIVELY by GitHub Actions**

**NEVER publish manually to JFrog Artifactory.** All publishing must go through GitHub Actions.

**Production Workflow:**

1. **Local Development**: Make changes and create version tag
   ```bash
   # Make your changes
   git add .
   git commit -m "feat: add new feature"

   # Let semantic-release create version tag
   FORCE_RELEASE=1 ./ci/ci publish  # Creates tag, pushes to GitHub
   ```

2. **GitHub Actions**: Automatically triggered by version tag push (`v*`)
   - Workflow: `.github/workflows/jfrog-publish.yml`
   - Builds package fresh from source (clean environment)
   - Publishes to JFrog using GitHub Secrets
   - Uses: `ARTIFACTORY_USERNAME`, `ARTIFACTORY_PASSWORD`

**Why GitHub Actions Only?**

- **Security**: JFrog credentials only in GitHub Secrets (never local)
- **Auditability**: All publishes tracked in GitHub Actions logs
- **Consistency**: Same build process for everyone
- **Single Source of Truth**: One place publishes, prevents conflicts
- **Clean Environment**: Fresh build every time, no local artifacts

**For Testing:**

The test suite (`tests/ci/test_ci.py`) includes `test_nuitka_publish_and_install()`
which validates the publish/install flow, but this is for CI validation only.
Production publishing must always use GitHub Actions.

**JFrog Authentication (Bootstrap Only):**

JFrog credentials in `.env` are used ONLY for bootstrap (installing dependencies).
**IMPORTANT**: Use ARTIFACTORY_* variables (matching GitHub Actions secrets):

1. **Username/Password (Primary)**:
   ```bash
   ARTIFACTORY_USERNAME=your-username
   ARTIFACTORY_PASSWORD=your-password
   ```

2. **Token Auth (Alternative)**:
   ```bash
   ARTIFACTORY_TOKEN=your-access-token
   ARTIFACTORY_TOKEN_USER=artifactory@hypersec.io  # Optional, default shown
   ```

**Migration from old JF_* variables**: Run `python migrate_env.py` to automatically update your .env file.

## Role in Forge Ecosystem

Hyperlib serves two roles:

1. **Production library**: Shared utilities for all HyperSec Python projects
2. **Template test case**: Real-world validation of forge-python package template

All changes to hyperlib that affect template structure should be documented in `docs/TEMPLATE-CHANGES.md` for backporting to forge-python.

## AI Assistant Knowledge Base - GitHub Actions

**Last Updated**: 2025-10-16 (Web search verified)
**Purpose**: Reference for AI assistants to avoid outdated assumptions

### GitHub Actions ARM64 Runners (2025)

**Availability** (as of August 2025 - Generally Available):

- **Public repositories**: ARM64 runners are **FREE** ✅
  - Labels: `ubuntu-24.04-arm`, `ubuntu-22.04-arm`
  - Specs: 4 vCPU, Cobalt 100 processors
  - Performance: Up to 40% faster than previous generation Azure ARM VMs
  - Status: Generally Available (GA as of August 2025)

- **Private repositories** (HyperSec uses private repos): Requires GitHub Team or Enterprise Cloud plan
  - Available as standard hosted runners (not "larger runners")
  - Labels: `ubuntu-24.04-arm`, `ubuntu-22.04-arm` (same as public)
  - Cost: Billed per minute (see pricing below)

**Pricing** (verified 2025) - **HyperSec private repositories**:

| Runner Type | vCPU | Cost/min | Cost/Build (7min) | Applies to HyperSec |
|-------------|------|----------|-------------------|---------------------|
| Linux x64 standard | 2 | $0.008 | $0.056 | ✅ Used |
| Linux ARM64 standard | 4 | $0.016 | $0.112 | ✅ Used (2x cost) |
| Linux ARM64 larger (8-core) | 8 | $0.02 | $0.14 | ❌ Not used |
| macOS ARM64 | 3 | $0.16 | $1.12 | ❌ Disabled (20x!) |

**Note**: Public repos get ARM64 for FREE, but HyperSec uses **private repositories** which are billed at $0.016/min for ARM64 (2x Linux x64 cost).

**Key Facts for AI Assistants (HyperSec Context)**:

1. ✅ **ARM64 runners ARE natively available** (not via QEMU emulation)
2. ⚠️ **HyperSec uses PRIVATE repositories** - ARM64 costs $0.016/min (2x Linux x64)
3. ✅ **Runner labels are stable**: `ubuntu-24.04-arm`, `ubuntu-22.04-arm`
4. ⚠️ **Requires GitHub Team/Enterprise plan** (HyperSec has this)
5. ⚠️ **macOS ARM64 is 20x more expensive** than Linux x64 - DISABLED by default
6. ⚠️ **Monthly cost** for private repos: ~$1.68/month (10 releases, x64 + ARM64)

**Workflow Configuration** (HyperSec private repos):

```yaml
# ARM64 runner for private repositories (billed at $0.016/min)
runs-on: ubuntu-24.04-arm
```

**Cost Optimization for HyperSec (Private Repos)**:

- **Linux x64**: Always enabled ($0.056 per build) ✅
- **Linux ARM64**: Enabled ($0.112 per build, 2x cost) ✅ - Provides ARM64 wheel distribution
- **macOS ARM64**: Disabled ($1.12 per build, 20x cost) ❌ - Only enable if absolutely needed
- **Monthly estimate**: $0.056 + $0.112 = $0.168 per release → ~$1.68/month (10 releases)
- **Alternative**: Self-hosted ARM64 runner (free but requires maintenance)

**Sources**:
- GitHub Changelog: "Linux arm64 hosted runners now available for free in public repositories" (Jan 2025)
- GitHub Changelog: "arm64 hosted runners for public repositories are now generally available" (Aug 2025)
- GitHub Docs: "About larger runners" (pricing details)

### Active Checking Strategy (CRITICAL for AI Assistants)

**PROBLEM**: Waiting with long timeouts (e.g., 10 minutes) only to discover the task failed in the first 2 seconds wastes time and causes frustration.

**SOLUTION**: Use `gh` CLI and `jf` CLI to **actively check progress** instead of passive waiting.

**Tools Available**:

1. **gh CLI** - GitHub Actions monitoring:
   ```bash
   gh run list --limit 5                    # List recent runs
   gh run view <run_id> --log              # View logs in real-time
   gh run watch <run_id>                   # Watch run progress
   gh workflow view <workflow_name>         # View workflow status
   ```

2. **jf CLI** - JFrog Artifactory verification:
   ```bash
   # Check if package exists in JFrog (requires JF_TOKEN/JF_USER in .env)
   jf rt search "hypersec-pypi-local/hyperlib/*" --count
   jf rt download "hypersec-pypi-local/hyperlib/<version>/*.whl" --dry-run
   ```

3. **Git remote status**:
   ```bash
   git log --oneline origin/main..HEAD     # Unpushed commits
   git status                               # Local changes
   ```

**Best Practices for AI Assistants**:

1. ✅ **Push and immediately check**: After `git push`, run `gh run list` to see if workflow started
2. ✅ **Check every 30-60 seconds**: Use `gh run view <run_id>` to check status, don't wait blindly
3. ✅ **Fail fast**: If logs show errors, stop waiting and investigate immediately
4. ✅ **Verify artifacts**: After build, check JFrog with `jf rt search` to confirm upload
5. ❌ **DON'T**: Set a 10-minute timer and hope for the best
6. ❌ **DON'T**: Assume success without verification

**Example Active Checking Workflow**:

```bash
# 1. Push changes
git push origin main

# 2. Immediately check if workflow started (within 10 seconds)
gh run list --limit 1

# 3. Get run ID and watch it
RUN_ID=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')
echo "Watching run: $RUN_ID"

# 4. Check every 30 seconds (don't wait 10 minutes!)
while true; do
  STATUS=$(gh run view $RUN_ID --json status,conclusion --jq '.status')
  echo "Status: $STATUS"

  if [ "$STATUS" = "completed" ]; then
    CONCLUSION=$(gh run view $RUN_ID --json conclusion --jq '.conclusion')
    echo "Conclusion: $CONCLUSION"
    break
  fi

  sleep 30
done

# 5. If successful, verify in JFrog immediately
jf rt search "hypersec-pypi-local/hyperlib/1.6.0/*.whl" --count
```

**Why This Matters**:

- GitHub Actions can fail due to: missing secrets, workflow syntax errors, runner unavailable
- JFrog uploads can fail due to: credentials, network, duplicate version
- **Early detection** saves time and prevents cascading failures
- **Active monitoring** provides immediate feedback for debugging

## Documentation

- **STATE.md** (this file) - Project state and instructions
- **README.md** - User-facing documentation
- **docs/ARTIFACTORY.md** - JFrog setup and publishing
- **docs/BOOTSTRAP-ANALYSIS.md** - Bootstrap implementation details
- **docs/TEMPLATE-CHANGES.md** - Template change tracking
- **TODO.md** - Task list
- **CHANGELOG.md** - Version history