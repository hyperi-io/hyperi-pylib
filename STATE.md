# Hyperlib - Project State

## ⚠️ CRITICAL: Git Commit Rules for This Project

**Hyperlib uses HyperCI as a git submodule at `/ci/`.**

### Commit to HyperCI Submodule (ci/ directory):

**CRITICAL:** All changes under `/ci/` MUST be committed to the **HyperCI repository**, not the hyperlib repository.

```bash
# For changes in ci/ directory:
cd ci
git add <files>
git commit -m "feat: description"
git push origin main

# Then update hyperlib to reference new ci/ commit:
cd ..
git add ci
git commit -m "chore: update ci submodule to <commit>"
git push origin main
```

**Files under `/ci/` go to:** https://github.com/hypersec-io/hyperci.git

### Commit to Hyperlib (everything else):

**All other files** (src/, tests/, pyproject.toml, README.md, etc.) go to the hyperlib repository:

```bash
# For changes outside ci/ directory:
git add <files>
git commit -m "feat: description"
git push origin main
```

**Files outside `/ci/` go to:** https://github.com/hypersec-io/hyperlib.git

### Summary:

- ✅ `/ci/` → commit to hyperci submodule first, then update hyperlib
- ✅ Everything else → commit to hyperlib
- ❌ NEVER commit `/ci/` changes directly to hyperlib (they go to hyperci!)

---

## SESSION STATUS (2025-10-21)

**Current State:** Complete HyperCI standardization with 4 modular tools

**Session Complete:** 104 commits (hyperlib: 100+, hyperci: 36+)

**Latest Achievements:**
✅ **Complete HyperCI Tool Suite** - 4 modular tools (bootstrap, run, ai, vcs)
✅ **Phase 1 & 2 Complete** - Modular /ci/ai + Multi-defaults Cascade
✅ **Code Standards** - CODE-ASSISTANT.md (965 lines), CODE_HEADER.md (REUSE/SPDX)
✅ **License System** - Apache 2.0, HyperSec EULA templates
✅ **Architecture** - modules/, run.d/, ai.d/, vcs.d/ (100% Linux convention)
✅ **Template Extraction** - Semantic suffix pattern throughout
✅ **Claude Tier Support** - Pro ($20/month) and Pro Max ($100-200/month)
✅ **Clean State Testing** - READ-ONLY ci/ verified from scratch
✅ **Git Commit Rules** - CRITICAL section added to STATE.md

**What Was Done Today:**
- ✅ Created hypersec-io/hyperci central repository (13 commits)
- ✅ Migrated hyperlib to use hyperci git submodule (28 commits)
- ✅ Implemented native uv mode (uv sync, uv build)
- ✅ Built Nuitka compiled wheels (556 KB with .so modules)
- ✅ Published to JFrog successfully
- ✅ Created extension system (ci-local/ for project-specific scripts)

**Pending Fix:**
- ⚠️ Test script needs pytest in .venv (currently only project deps)
- See TODO.md Priority 1 for solution

**Ready For:**
- DFE project pilot (dfe-hunt-runner)
- GitHub Actions testing (needs GH_PAT secret)

---

## CRITICAL: Read Documentation First

<!--
AI AGENTS: Read these files BEFORE starting work:
1. STATE.md (or CLAUDE.md symlink) - THIS FILE
2. TODO.md - Current priorities and pending work
3. HyperCI section below - ci/ is git submodule from hypersec-io/hyperci
4. ci/docs/SESSION-SUMMARY.md - What was accomplished this session
5. ci/docs/README.md - HyperCI complete guide
6. ci/docs/SUBMODULE-USAGE.md - Git submodule operations
7. docs/CHARS-POLICY.md - Character restrictions (ASCII logs, limited emoji)
8. ci/docs/JFROG.md - JFrog publishing
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

**CRITICAL**: Hyperlib uses [HyperCI](https://github.com/hypersec-io/hyperci) via **git submodule**.

### Architecture

The `ci/` directory is a git submodule pointing to `hypersec-io/hyperci`:
- **Central Repo**: https://github.com/hypersec-io/hyperci
- **Method**: Git submodule (reference to hyperci repo)
- **Pin Version**: `cd ci && git checkout v1.0.0` (explicit version control)
- **Updates**: `cd ci && git pull origin main` (standard git workflow)
- **Configuration**: `ci.yaml` at project root (project-specific, NOT in submodule)

### What This Means

**CI Scripts are Centralized:**
- ✅ All `ci/` scripts come from hyperci repo (via submodule)
- ✅ Bootstrap, build, test, Nuitka scripts shared across ALL projects
- ✅ Updates to hyperci available to all projects (explicit pull)
- ✅ One fix in hyperci → all projects can update
- ✅ Version pinning: Each project controls which hyperci version to use

**Configuration is Project-Specific:**
- ✅ Each project has `ci.yaml` at project root (NOT in ci/ submodule)
- ✅ Managed independently from hyperci updates
- ✅ Hyperlib's `ci.yaml` stays under version control in this repo

### Updating HyperCI

```bash
# Update to latest hyperci
cd ci
git pull origin main
cd ..
git add ci
git commit -m "chore: update hyperci submodule to latest"

# Or pin to specific version
cd ci
git checkout v1.2.0  # Pin to tagged version
cd ..
git add ci
git commit -m "chore: pin hyperci to v1.2.0"

# Test after update
./ci/bootstrap --install
ci/.venv/bin/python ci/python/ci.d/20-python-test.py check
```

### Contributing Back to HyperCI

```bash
# If you improve a script in hyperlib's ci/ submodule:
cd ci
git checkout -b fix/my-improvement
# Make changes
git add .
git commit -m "fix: my improvement"
git push origin fix/my-improvement
cd ..

# Create PR in hyperci repo
gh pr create --repo hypersec-io/hyperci

# After merge, update hyperlib to use new version
cd ci
git pull origin main
cd ..
git add ci
git commit -m "chore: update hyperci with my-improvement"
```

**See Also**:
- [ci/docs/SUBMODULE-USAGE.md](ci/docs/SUBMODULE-USAGE.md) - Submodule operations
- [ci/docs/PROJECT-EXTENSIONS.md](ci/docs/PROJECT-EXTENSIONS.md) - Custom scripts (ci-local/)
- [ci/docs/README.md](ci/docs/README.md) - Complete HyperCI documentation
- [ci/docs/MIGRATE-dfe-hunt-runner.md](ci/docs/MIGRATE-dfe-hunt-runner.md) - Migration guide example

### Native UV Mode (Automatic!)

**CRITICAL:** HyperCI now auto-detects and uses native uv mode.

**Hyperlib has `uv.lock`**, so bootstrap automatically uses:
- ✅ `uv sync --locked` (respects uv.lock → reproducible builds)
- ✅ `uv build` (native uv build → faster than python -m build)

**Auto-detection:**
- Detects `uv.lock` → uses native uv commands
- No `uv.lock` → uses pip compatibility mode

**Benefits:**
- ✅ Reproducible (exact versions from uv.lock)
- ✅ Faster (no dependency resolution)
- ✅ Compatible with DFE projects (all use uv.lock)
- ✅ No configuration needed (just works!)

## Claude Code Setup (Optional)

**CRITICAL**: HyperCI can automatically configure Claude Code settings for your project.

### Requirements

**Node.js and npx** are required for Claude Code:
- Claude Code runs on Node.js runtime
- npx is used for package execution
- Install: https://nodejs.org/ (includes npx)

**Verification:**
```bash
# Bootstrap automatically checks during --install
./ci/bootstrap --install
# If Node.js missing, bootstrap will fail with clear error

# Manual check
node --version && npx --version
```

**If Node.js is not available:**
- Bootstrap will fail during Claude settings merge (if `CI_CLAUDE_MERGE != skip`)
- Error message provides installation instructions
- To skip Claude setup: `CI_CLAUDE_MERGE=skip ./ci/bootstrap --install`

### CI_CLAUDE_MERGE Environment Variable

Controls whether HyperCI's standardized Claude Code settings are merged into your `.claude/` directory.

**Modes:**
- `CI_CLAUDE_MERGE=skip` (default) - No automatic merge (opt-in model)
- `CI_CLAUDE_MERGE=merge` - Merge and overwrite existing settings
- `CI_CLAUDE_MERGE=no-overwrite` - Merge but keep existing values

**Usage:**
```bash
# Enable Claude settings merge during bootstrap
CI_CLAUDE_MERGE=merge ./ci/bootstrap --install
```

### What Gets Merged

**1. settings.json** (Deep JSON merge)
- **From ci/common/claude/settings.json**: Universal settings
  - Environment variables (ripgrep, parallel tools, context window)
  - Permissions (READ-ONLY ci/** enforcement)
  - SessionStart hooks (displays STATE.md/TODO.md on start)
  - Plugin settings
- **From ci/python/claude/settings.json**: Python-specific settings
  - Python model defaults (sonnet, 8K tokens)
  - Python tool permissions (pytest, ruff, black, etc.)

**2. STATE.md** (Idempotent append with markers)
- **From ci/common/claude/STATE.md**: Common CI documentation
  - HyperCI architecture
  - Bootstrap process
  - Virtual environment separation
  - Git submodule operations
- **From ci/python/claude/STATE.md**: Python CI documentation
  - Semantic versioning workflow
  - Testing, building, publishing
  - Nuitka builds
  - Python best practices

**3. TODO.md** (Template creation if missing)
- **From ci/common/claude/TODO.md**: Standardized TODO template
  - Follows todo-md standard (github.com/todo-md/todo-md)
  - Sections: Active, Planned, Done, Backlog
  - Format guide and Claude Code integration tips
  - **SAFETY**: Only creates if TODO.md doesn't exist (never overwrites)

**4. commands/*.md** (Slash commands)
- Custom slash commands from ci/ and ci-local/

### Safety Guarantees

✅ **Idempotent**: Running multiple times is safe (no duplicates)
✅ **Non-destructive**: Never overwrites TODO.md
✅ **Marker-based**: STATE.md uses HTML comments to prevent duplicate appends
✅ **Opt-in**: Default is `skip` (user must explicitly enable)
✅ **Mergeable**: settings.json uses deep merge (preserves existing keys)

### Example Workflow

```bash
# First time setup
CI_CLAUDE_MERGE=merge ./ci/bootstrap --install

# This will:
# 1. Merge settings.json (adds HyperCI defaults)
# 2. Append STATE.md (adds CI documentation)
# 3. Create TODO.md if missing (from template)
# 4. Copy slash commands

# Future bootstrap runs (default: skip)
./ci/bootstrap --install  # Won't touch Claude settings

# To update Claude settings later
CI_CLAUDE_MERGE=merge ./ci/bootstrap --install  # Safe to rerun
```

## /ci/ai Tool - AI Assistant Setup

**HyperCI provides the `/ci/ai` tool for configuring AI assistant settings** (Claude Code, etc.).

This tool is the modern replacement for `CI_CLAUDE_MERGE` environment variable.

### Quick Start

```bash
# Check AI assistant configuration
ci/ai check

# Setup AI assistant (merge settings, MCP servers, docs)
CI_AI_MERGE_MODE=merge ci/ai setup

# Clean AI assistant configuration
ci/ai clean
```

### Configuration Cascade

The `/ci/ai` tool uses the standardized HyperCI config cascade:

```
ENV > .env > ci.yaml > defaults
```

**Environment Variables:**
- `CI_AI_MERGE_MODE` - Controls merge behavior (skip, merge, no-overwrite, force)
- `CI_AI_CLAUDE_TIER` - Claude tier selection (pro, pro-max)
- `CI_AI_CHECK_REQUIREMENTS` - Enable/disable Node.js/npx check
- `CI_AI_SETUP_MCP` - Enable/disable MCP server setup
- `CI_AI_MCP_MEMORY_PATH` - Custom memory directory path

**ci.yaml Configuration:**
```yaml
# ci-local/ci.yaml
ai:
  merge_mode: skip  # Options: skip, merge, no-overwrite, force
  claude_tier: pro-max  # Options: pro, pro-max
  check_requirements: true
  mcp:
    enabled: true
    servers:
      sequential_thinking:
        enabled: true
        package: "@modelcontextprotocol/server-sequential-thinking"
      memory:
        enabled: true
        package: "mcp-knowledge-graph"
        memory_path: ".claude/claude-memory"
```

### Merge Modes

**skip** (default):
- No automatic merge (opt-in model)
- Safest option, requires explicit enable

**merge**:
- Deep merge settings.json (overwrites existing keys)
- Appends STATE.md (idempotent with markers)
- Creates TODO.md if missing (never overwrites)
- Copies standards to docs/standards/

**no-overwrite**:
- Deep merge settings.json (keeps existing values)
- Same as merge but preserves your custom settings

**force**:
- Like merge but also overwrites TODO.md
- **DANGEROUS** - Only use for testing

### What ci/ai setup Does

**1. Check Requirements** (10-check-requirements.py)
- Verifies Node.js and npx are available
- Required for MCP servers
- Skippable: `CI_AI_CHECK_REQUIREMENTS=false`

**2. Setup MCP Servers** (15-setup-mcp-servers.py)
- Installs sequential-thinking server (structured reasoning)
- Installs memory server (knowledge graph)
- Creates memory directory (.claude/claude-memory/)
- Skippable: `CI_AI_SETUP_MCP=false`

**3. Merge Settings** (20-merge-settings.py)
- Deep merges settings-claude-{tier}.json
- Supports: pro ($20/month, 4K tokens) or pro-max ($100-200/month, 16K tokens)
- Template substitution: {{PROJECT_ROOT}}

**4. Append STATE.md** (30-append-state.py)
- Appends CI documentation from ci/
- Idempotent (uses HTML markers)
- Covers: HyperCI architecture, bootstrap, config cascade

**5. Create TODO.md** (40-create-todo.py)
- Creates from template if missing
- NEVER overwrites existing TODO.md (unless force mode)
- Follows todo-md standard

**6. Copy Standards** (50-copy-standards.py)
- Copies/merges docs/standards/*.md
- Includes CODE-ASSISTANT.md (965+ lines)
- Merges multiple sources (common + python)

### Examples

```bash
# First time setup (merge all settings)
CI_AI_MERGE_MODE=merge ci/ai setup

# Update settings without overwriting customizations
CI_AI_MERGE_MODE=no-overwrite ci/ai setup

# Setup with pro tier (default is pro-max)
CI_AI_CLAUDE_TIER=pro CI_AI_MERGE_MODE=merge ci/ai setup

# Setup without MCP servers
CI_AI_SETUP_MCP=false CI_AI_MERGE_MODE=merge ci/ai setup

# Clean all AI assistant config
ci/ai clean
```

### Migration from CI_CLAUDE_MERGE

**Old (deprecated):**
```bash
CI_CLAUDE_MERGE=merge ./ci/bootstrap --install
```

**New (recommended):**
```bash
CI_AI_MERGE_MODE=merge ci/ai setup
# Or add to ci.yaml for permanent configuration
```

**Backward Compatibility:**
- `CI_CLAUDE_MERGE` still works (mapped to `CI_AI_MERGE_MODE`)
- Both will be supported for transition period
- New projects should use `ci/ai` tool exclusively

## Bootstrap (ALWAYS Run First)

**Setup**: `./ci/bootstrap --install` | **Check**: `./ci/bootstrap`

### Project Type Auto-detection

**Bootstrap automatically detects project type** on first run (when `ci.yaml` doesn't exist).

**Detection logic** (from `pyproject.toml`):
- **package** (library): No entry points → `build_type: package` (compiled wheels)
- **app** (application): Has `project.scripts` or `project.gui-scripts` → `build_type: app` (standalone binary)

**Override mechanism:**
- Auto-detection only runs ONCE (first bootstrap)
- Creates `ci.yaml` with detected type
- User can manually edit `ci.yaml` to override:
  ```yaml
  nuitka:
    build_type: app  # Changed from package
  ```
- Future bootstrap runs respect manual `ci.yaml` settings

**Example:**
```bash
# First bootstrap
./ci/bootstrap --install
# → Detects "package" (no entry points)
# → Creates ci.yaml with build_type: package

# User edits ci.yaml manually
vim ci.yaml  # Change build_type to "app"

# Future bootstrap
./ci/bootstrap --install
# → Uses "app" (respects ci.yaml override)
```

**Configuration cascade:**
1. `ci.yaml` (project-specific, highest priority)
2. Environment variables (`CI_*` overrides)
3. Defaults from auto-detection

**3 Phases**:
1. System Python creates `ci-local/.venv` (NOT ci/.venv - ci/ is READ-ONLY!)
2. Installs CI tools into ci-local/.venv (via `uv sync` from ci-local/uv.lock)
3. Runs `bootstrap.d/*` scripts (common + python + ci-local/ for extensions)

**Requires**: `.env` with `JF_USER`/`JF_PASSWORD`, Python 3.11+, JFrog network access

**Installs**: `ci-local/.venv` (CI tools), `.venv` (project dependencies from uv.lock)

### Virtual Environment (CRITICAL - READ CAREFULLY)

**Two COMPLETELY SEPARATE environments exist. NEVER mix them!**

#### ci-local/.venv (CI Tools ONLY) ← NEW!
- **Purpose**: CI tools for testing, linting, building, releasing
- **Created by**: `ci/bootstrap --install`
- **Contains**: pytest, ruff, black, mypy, build, twine, semantic-release, dynaconf (CI tools ONLY)
- **Does NOT contain**: Project dependencies (your app's dynaconf, loguru, etc.)
- **Source**: `ci-local/pyproject.toml` (project-specific CI tools)
- **Lock**: `ci-local/uv.lock` (committed, reproducible)
- **Usage**: CI scripts ONLY (`ci-local/.venv/bin/python ci/python/ci.d/*.py`)
- **Location**: ci-local/.venv (WRITABLE, gitignored)
- **Never activate manually**

**CRITICAL: ci/ is READ-ONLY for everything, including .venv!**
All operational writes go to ci-local/ (not ci/)

#### .venv (Project Dependencies)
- **Purpose**: Project runtime dependencies + development tools
- **Created by**: `ci/bootstrap --install` (automatic via uv)
- **Contains**: Project dependencies (dynaconf, loguru, pyyaml, psutil, etc.)
- **Does NOT contain**: CI-specific tools (those are in ci-local/.venv)
- **Source**: `uv.lock` (at project root, committed)
- **Installation**: `uv sync --all-extras --all-groups` (reproducible from uv.lock)
- **Usage**: Development, IDE, manual testing
- **Can activate**: `source .venv/bin/activate` for interactive use
- **Lock file**: `uv.lock` (committed, tracks exact versions)

#### Protection Mechanisms (Enforced Separation)
1. **Complete READ-ONLY ci/**: No .venv creation in ci/ directory
2. **ci-local/.venv**: All CI tool installations go here
3. **Marker files** - Identify venv purpose
4. **Runtime checks** - Every CI script validates venv path
5. **CI runner enforcement** - All scripts use ci-local/.venv explicit path
6. **Documentation** - This section and README files
7. **Gitignore** - ci-local/.venv ignored (ci/.venv removed from ci/.gitignore)

#### For AI Assistants / LLMs - CRITICAL RULES

**CRITICAL: ci/ is READ-ONLY for EVERYTHING (including .venv creation)**

**When writing CI scripts:**
- ✅ ALWAYS use: `ci-local/.venv/bin/python` for CI operations
- ✅ ALWAYS check: Script prefix contains "ci-local/.venv"
- ✅ CI tools live in: `ci-local/.venv` (NOT ci/.venv)
- ✅ CI scripts are in: `ci/` (READ-ONLY)
- ❌ NEVER write to: `ci/` directory (including ci/.venv)
- ❌ NEVER use: `#!/usr/bin/env python3` without checks
- ❌ NEVER use: `python` or `python3` commands
- ❌ NEVER use: `.venv` for CI

**When writing development code:**
- ✅ Use `.venv/bin/python` or activate `.venv`
- ✅ For manual testing and exploration only
- ❌ NEVER use `ci-local/.venv` for development
- ❌ NEVER install dev dependencies in `ci-local/.venv`

**How to check which venv:**
```bash
# Before running any command, verify:
echo $VIRTUAL_ENV           # Should show ci-local/.venv or .venv
echo $VENV_PURPOSE          # Should show 'ci' or 'dev'
python -c "import sys; print(sys.prefix)"  # Check Python location
```

**Why ci-local/.venv (not ci/.venv):**
- ci/ is a git submodule and must be READ-ONLY for all operations
- ci-local/ is project-writable space for CI tools, configs, and venvs
- This enforces clean separation: ci/ (scripts, READ-ONLY) vs ci-local/ (data, WRITABLE)

## Universal Policies

### Temporary Files
Use `./.tmp/` only (not `/tmp`, `~/tmp`, `/var/tmp`)

### TODO
`TODO.md` is single source of truth (lightweight Markdown, updated directly by LLM)

### Bash Command Execution Policy

**CRITICAL: Avoid command chaining to prevent approval prompts**

The following patterns require user approval:
- `Bash("command1 && command2")` (chained with &&)
- `Bash("command1 ; command2")` (chained with ;)

**Instead, use sequential Bash calls:**

```python
# ❌ BAD - Triggers approval prompt
Bash("git add . && git commit -m 'msg'")

# ✅ GOOD - Sequential execution
Bash("git add .")
Bash("git commit -m 'msg'")
```

**Why this matters:**
- Command chaining with `&&` or `;` triggers Claude Code's permission system
- Sequential calls execute the same logic without requiring approval
- Use `&&` in a single tool call ONLY when both commands must be atomic

**Exception:** Chain commands with `&&` when atomicity is required (e.g., `cd dir && command` where command MUST run in dir).

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

Current version: **2.2.0**

### Dual Pre-sync Strategy (VERSION Corruption Prevention)

**CRITICAL**: Hyperlib implements a **dual pre-sync strategy** to prevent VERSION file corruption during semantic-release.

**The Problem**:
- Semantic-release uses `{version}` template in `build_command`
- If build fails, `{version}` literal can get written to VERSION file
- This corrupts the VERSION file and breaks future releases

**The Solution - Dual Pre-sync**:

**Option 1: Pre-commit Hook** ([.git/hooks/pre-commit](.git/hooks/pre-commit))
- Runs BEFORE every commit on `main`/`master` branches
- Calls `semantic-release version --print` to get next version
- Pre-syncs VERSION file BEFORE commit is created
- **Benefit**: Local commits already have correct VERSION

**Option 2: CI Pre-sync Script** ([ci-local/common/ci.d/89-version-pre-sync.py](ci-local/common/ci.d/89-version-pre-sync.py))
- Runs BEFORE semantic-release in CI environments
- Uses `semantic-release version --print` to get next version
- Pre-syncs VERSION file before semantic-release modifies pyproject.toml
- **Benefit**: CI releases are protected even if pre-commit hook didn't run

**Architecture**:
```
ci-local/
├── common/
│   ├── ci_local_lib.py               # Helper functions (get_next_semantic_version, etc.)
│   └── ci.d/
│       └── 89-version-pre-sync.py    # Common layer - handles VERSION file (ALL project types)
└── python/
    └── ci.d/
        └── 89-python-version-sync.py # Python layer - validates pyproject.toml/__init__.py
```

**Layered Design**:
- **Common layer** (89-version-pre-sync.py): Handles VERSION file for ALL project types (Python, Node.js, Go, etc.)
- **Python layer** (89-python-version-sync.py): Validates Python-specific files (pyproject.toml, __init__.py)
- **Separation of concerns**: Common functionality separate from language-specific logic

**How It Works**:

1. **Developer makes commit with conventional commit message**:
   ```bash
   git commit -m "fix: prevent VERSION corruption"
   ```

2. **Pre-commit hook runs automatically**:
   - Detects commit is on `main`/`master`
   - Runs `semantic-release version --print` → gets "2.2.0"
   - Writes "2.2.0" to VERSION file
   - Stages VERSION in the commit

3. **Commit completes with correct VERSION**

4. **Later, semantic-release runs (manual or CI)**:
   - Updates pyproject.toml and __init__.py to "2.2.0"
   - Runs build_command (which no longer needs to write VERSION)
   - Creates release commit and tag
   - Pushes to GitHub (if CI_PUSH=1)

**Build Command**:
```toml
# pyproject.toml
build_command = "echo 'VERSION already synced by pre-commit hook/CI script' && rm -rf dist build src/*.egg-info && ci-local/.venv/bin/python -m build"
```

**Benefits**:
- ✅ **No VERSION corruption** - Pre-sync ensures VERSION is always correct
- ✅ **No shell escaping issues** - build_command doesn't need to handle {version} template
- ✅ **Fail-fast** - If semantic-release fails, VERSION is already correct
- ✅ **Dual protection** - Both local (pre-commit hook) and CI (script) coverage
- ✅ **Language-agnostic** - Common layer works for any project type

**Disabling**:
```bash
# Skip pre-sync (for testing)
CI_SKIP_VERSION_SYNC=1 git commit -m "fix: test without pre-sync"
```

**Testing**:
```bash
# Test pre-commit hook
git commit -m "fix: test pre-sync"  # VERSION should be auto-updated

# Test CI script
CI_FORCE_RELEASE=1 ci-local/.venv/bin/python ci/common/ci.d/90-semantic-release.py release
```

**Recovery** (if VERSION gets corrupted):
```bash
# Manual fix
echo "2.2.0" > VERSION

# Or use recovery script
ci-local/.venv/bin/python ci-local/python/ci.d/99-fix-version.py fix
```

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
- **ci/docs/JFROG.md** - JFrog setup and publishing
- **ci/docs/BOOTSTRAP-INTERNALS.md** - Bootstrap implementation details
- **docs/TEMPLATE-CHANGES.md** - Template change tracking
- **TODO.md** - Task list
- **CHANGELOG.md** - Version history

---

