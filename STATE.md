# hs-lib - Project State

**Repository**: https://github.com/hypersec-io/hs-lib
**Type**: Python package (shared library)
**Purpose**: Enterprise infrastructure for all HyperSec Python projects

---

## 🔄 SESSION MANAGEMENT

**IMPORTANT:** If this is a new session or context was compressed:
1. **Run `/start` command** to initialize the session properly
2. Read STATE.md, TODO.md, and standards documentation
3. Confirm ready before proceeding with work

**Save progress anytime:** Run `/save` to checkpoint progress, clean up STATE.md and TODO.md

---

## Current Status (2025-11-18)

**Versions:**
- hs-lib: v2.9.0 (released)
- hs-ci: v1.10.1+ (Nuitka app build support)

**Active work:**
- Nuitka app build: COMPLETE ✅ (tested and working)
- Ready for downstream project updates (see TODO.md)

**Test status:** 339 passed, 16 skipped, 0 failed

---

## Session 2025-11-18 - Nuitka App Build Implementation

### Nuitka App Build - Complete ✅

**Working end-to-end** for CLI applications with `build_type: app`:
- Binary: test-cli-linux-x64.bin (14MB, encrypted)
- Local testing: `./ci/bootstrap install --local-build && ./ci/run build --nuitka --local-build`
- GitHub Actions: Automatic on v* tag push (BuildJet runners)
- Protection: Nuitka Commercial with full encryption

**Test project:** /projects/test-cli-build (test CLI app using hs-lib)

**Major fixes (30+ commits to hs-ci):**
1. --local-build flag for local Nuitka testing (avoids slow GitHub Actions feedback)
2. Fixed critical indentation bug (nuitka-commercial install was conditional)
3. Script ordering: 36-nuitka runs AFTER uv sync (prevents removal)
4. Auto-detect entry points: main.py, __main__.py, app.py, cli.py
5. Auto-detect package names (no hardcoded "hyperlib")
6. Enforce nuitka-commercial ONLY (OSS Nuitka fails hard)
7. JFrog private PyPI ONLY (removed public PyPI fallback - security)
8. Install pycryptodomex for traceback-encryption plugin
9. libatomic-static checks (bootstrap + GitHub Actions)
10. Pass source directory to Nuitka (not __init__.py)
11. Add build and twine to pyproject.toml template

**CI Architecture improvements:**
- Split 30-python-test.py → 30-python-lint.py + 35-python-test.py
- linters/tests config separation (independent control)
- Rename 52-verify-publish → 60-verify-publish (runs after Nuitka)
- JFrog PyPI enforcement with cascade detection
- Simplified ci readonly detection (submodule check only)
- Minimal hs-lib ci.yaml (7 lines, only non-defaults)

**Configuration cascade:**
- `python.build_type: app` → Nuitka inherits (no duplication)
- `linters.required: true, fail_fast: true` (defaults)
- `tests.required: true, fail_fast: true` (defaults)

**Next steps:**
- Test Nuitka package builds (build_type: package)
- GitHub Actions/BuildJet release testing
- Implement linters.checklist selective execution
- Remove hardcoded Python versions (use cascade)

---

## Session 2025-11-15-B - Complete Package Rename and Release

### Package Rename Complete ✅

**Complete elimination of all "hyperlib" and "hyperci" references:**
- 112 files updated (384 insertions, 418 deletions)
- Zero "hyperlib" references (case-insensitive verification)
- Zero "hyperci" references (case-insensitive verification)

**Changes:**
- Package: hyperlib → hs-lib (PyPI, imports, all docs)
- Environment variables: HYPERLIB_* → HS_LIB_* (HS_LIB_PROFILE, HS_LIB_DEBUG, etc.)
- HELM chart: hyperlib-app → hs-lib-app (directory + all templates)
- Test identifiers: hs_lib- → hs-lib- (Kubernetes RFC 1123 compliance)
- Log paths: hyperlib.log → hs-lib.log

**Bug fixes:**
- Fixed shutdown handler registration with FastAPI event system
- Handler now properly registered with add_event_handler()
- All e2e tests passing

### Release v2.9.0 ✅

**Version:** v2.9.0 (MINOR bump - feat: commits in history)
- Previous: v2.8.8
- Avoided major bump by removing BREAKING CHANGE footers from git history

**Published:**
- GitHub: v2.9.0 marked as "Latest"
- JFrog PyPI: hs-lib v2.9.0 published
- Build artifacts: hs_lib-2.9.0-py3-none-any.whl, hs_lib-2.9.0.tar.gz

**Cleanup:**
- Deleted v3.0.0 from GitHub, Git, and JFrog
- Git history cleaned (BREAKING CHANGE footers removed via filter-branch)
- Build artifacts cleaned

### Critical Lesson: Semantic Versioning

**Problem:** Multiple accidental v3.0.0 major bumps
**Cause:** "BREAKING CHANGE:" footers in old commits
**Solution:** Used git filter-branch to remove BREAKING CHANGE footers from history
**Takeaway:** Be extremely careful with commit message footers - they affect semantic versioning

---

## Session 2025-11-15-A - CI and AI Finalization

### Claude Code 2.0 Permission System - Complete ✅

**Dual-pattern Bash permissions:**
- Researched Claude Code 2.0 syntax (colon `:*` operator)
- Colon operator means "continuation from preceding string"
- Implemented both `Bash(command *)` AND `Bash(command:*)` patterns
- Comprehensive coverage: git, uv, pytest, docker, kubectl, all dev tools
- SlashCommand permissions for `/start` and `/save`

**Key fix:** `git -C` permission (major pain point for submodule work)

**Files updated:**
- [ci/modules/common/templates/settings.json](ci/modules/common/templates/settings.json) - Template with all permissions
- [.claude/settings.json](.claude/settings.json) - Local with dual patterns (gitignored)

### Python 3.12 Migration - Complete ✅

**Updated across both repositories:**
- ✅ hs-lib requires Python 3.12
- ✅ hs-ci templates require Python 3.12
- ✅ All tool configs (ruff, black, pyright, mypy)
- ✅ Fixed duplicate pytest markers in hs-lib

**Critical lesson:** Removed "Breaking change:" from commit to avoid v2.0.0 major bump
- Deleted v2.0.0 release
- Rewrote git history to remove breaking change marker
- Re-released as v1.6.12 (patch, correct)
- Python version updates are NOT breaking (gradual adoption)

### Repository Rename - Complete ✅

**hs-ci (formerly hs-ci):**
- ✅ Repository URL in .releaserc.json
- ✅ All documentation updated
- ✅ Generic templates (PROJECT_NAME)
- ✅ Workflow now passing (was failing due to URL mismatch)

**hs-lib (formerly hs-lib):**
- ✅ README badges updated (removed version badge, Python 3.12+)
- ✅ All documentation renamed
- ✅ Examples updated
- ✅ Strong WIP warning for Application framework

### Settings Cleanup - Complete ✅

- ✅ Removed settings.local.json from deployment (obsolete)
- ✅ ENV vars now in ~/.bashrc (via 20-bashrc-env.py)
- ✅ Removed .pip/pip.conf from git tracking (credentials)
- ✅ Verified .pip/ properly gitignored

### Documentation Rationalization - Complete ✅

**Massive cleanup:**
- hs-lib STATE.md: 3191 → 118 lines (96% reduction!)
- hs-lib TODO.md: 1164 → 83 lines (93% reduction!)
- hs-ci STATE.md: 559 → 119 lines (78% reduction!)
- **Total: Removed 4273 lines of stale content**

**Standards consolidation:**
- Merged Derek's communication preferences into AI-GUIDELINES.md
- Consolidated Australian/American English spelling guide
- Removed duplicate Communication Style from COMMON.md
- Clear separation: COMMON = workflow, AI-GUIDELINES = code quality

### File Structure Clarity

**code-assistant/ standards:**
- **COMMON.md** - Workflow, process, session management, tools
- **AI-GUIDELINES.md** - Code quality, communication style, spelling guide
- **HS-CI.md** - HS-CI specific workflow
- **PYTHON.md** - Python specific guidance

**ci-local/code-assistant/:**
- **DEREK-PREFERENCES.md** - Derek's personal preferences (loaded by `/start`)

---

## Architecture Notes

### hs-ci Release System (Two Separate Systems)

**1. hs-ci ITSELF:**
- Automation: semantic-release CLI + .releaserc.json (Node.js)
- Avoids circular dependency

**2. hs-ci AS A SERVICE:**
- Automation: Python-based `./ci/run release`
- Full orchestration for parent projects

---

## Quick Reference

**Python requirement:** 3.12+

**Test command:** `./ci/run check`

**Update ci:** `cd ci && git pull origin main && cd .. && git add ci && git commit -m "chore: update hs-ci submodule"`

---

**Last Updated:** 2025-11-15


---

<!-- HYPERCI_STATE_MD: HYPERCI_STATE_MD: ci/modules/common/templates/STATE.md -->
# HyperCI - Common CI/CD Documentation

**Auto-appended to project STATE.md during AI setup**

## Critical Policies for AI Assistants

**ALWAYS READ ON SESSION START:**
1. This STATE.md file (you're reading it now)
2. `TODO.md` (current tasks and priorities)
3. **Use `/start` command** - Automatically loads all mandatory files below

**Mandatory files loaded by `/start`:**
- `ci/docs/standards/STANDARDS.md` - Entry point with LLM RAG strategy
- `ci/docs/standards/code-assistant/COMMON.md` - Session mgmt, bash, commits (ALWAYS)
- `ci/docs/standards/code-assistant/HYPERCI.md` - CI infrastructure guidance (IF working on CI)
- `ci/docs/standards/code-assistant/PYTHON.md` - Python guidance (IF Python project)
- `ci/docs/standards/common/CHARS-POLICY.md` - Character restrictions (ALWAYS)
- `ci/docs/standards/common/CODE-HEADER.md` - File headers (ALWAYS)
- `ci/docs/standards/common/GIT-WORKFLOW.md` - Git conventions (ALWAYS)
- `ci/docs/standards/common/QUICK-REFERENCE.md` - Cheat sheet (ALWAYS)
- `ci-local/ai/*.md` - Project/developer overrides (if any exist)

**Context-specific files (loaded by `/start` based on project type):**
- Python: `ci/docs/standards/python/CODING.md`
- Containerization: `ci/docs/standards/common/CONTAINERIZATION.md`

**Do not skip the `/start` command. It ensures consistent CAG (Code Assistant Guidance) loading.**

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
- `.env` - Credentials (gitignored)
- `ci-local/ci.yaml` - Project CI configuration

**Project workspace:**
- `.venv/` - Unified venv for project + CI tools (uv-managed)
- `pyproject.toml` - Project metadata + CI tool configs
- `.tmp/` - Temporary files (ALWAYS use this, not /tmp)

### 3. AI Guidance Architecture (Merge Only When Must)

**CRITICAL PRINCIPLE: Read directly from source, merge ONLY when we MUST.**

**File locations:**
- **Core guidance (read-only):** `ci/docs/standards/ai/*.md`
  - CODE-ASSISTANT-COMMON.md - Universal guidance for all projects
  - CODE-ASSISTANT-HYPERCI.md - CI infrastructure work only
  - CODE-ASSISTANT-PYTHON.md - Python-specific guidance (if exists)
  - Always read directly from ci/ (no copying)

- **Project overrides (writable):** `ci-local/ai/*.md`
  - User/project-specific guidance
  - Developer customizations
  - Supplements (doesn't replace) core guidance

**Why this matters:**
- ✅ **Simpler:** No merge logic, no conflicts, no duplication
- ✅ **Single source of truth:** Core guidance always in ci/docs/standards/
- ✅ **Easy updates:** Pull ci/ submodule to get latest guidance
- ✅ **Flexibility:** Users can add custom guidance without modifying ci/

**When files ARE merged (exceptions only):**
- `STATE.md` - Appends CI documentation to bottom (marker: HYPERCI_STATE_MD)
- `.claude/settings.json` - Merges basic + tier-specific settings
- Both use markers to detect and replace sections cleanly

**When files are COPIED (versioned templates):**
- `.claude/commands/start.md` - Slash command (copy-overwrite, always latest)
- `.claude/commands/save.md` - Slash command (copy-overwrite, always latest)

**Default pattern for new files:** Read directly from ci/ (no copy, no merge)

### 4. Virtual Environment

**ONE unified .venv (project root):**
- Contains both project dependencies AND CI tools
- Managed by `uv` (fast, reliable)
- CI dependencies auto-installed by bootstrap:
  - dynaconf (config management)
  - pyyaml (YAML parsing)
  - tomli + tomli-w (TOML read/write)
  - python-semantic-release (versioning)

**CI scripts use .venv/bin/python:**
All CI tools run in the same venv as your project.

### 5. Bootstrap & Workflow

**Bootstrap (first-time setup):**
```bash
./ci/bootstrap install                # Install CI tools + Git hooks (RECOMMENDED)
./ci/bootstrap install --ai           # Install CI tools + Git hooks + AI setup
```

Creates .venv, installs dependencies, and sets up Git hooks. Use `--ai` to also install AI files.

**Run CI checks:**
```bash
./ci/run check       # All checks (tests, lint, type-check)
./ci/run test        # Tests only
./ci/run build       # Build package
```

**Git hooks (auto-installed by bootstrap):**
- `commit-msg` - Validates branch name, message format, removes AI attribution
- Blocks commits if invalid, warns about formatting issues

### 6. CI Script Locations

**New modular structure:**
```
ci/modules/
├── common/
│   ├── bootstrap.d/     # Bootstrap scripts (run during setup)
│   ├── run.d/           # Runtime checks (branch name, etc.)
│   ├── hooks/           # Git hooks (installed by bootstrap)
│   └── templates/       # File templates (.gitignore, etc.)
└── python/
    ├── bootstrap.d/     # Python bootstrap scripts
    └── run.d/           # Python CI checks (test, build, etc.)
```

**Execution:** All CI scripts run via bash wrappers using `.d` pattern
- `ci/bootstrap` orchestrates `bootstrap.d/*.py` scripts (includes git hooks)
- `ci/run` orchestrates `run.d/*.py` scripts

### 7. TODO Management

**Use TODO.md ONLY:**
- ✅ Add todos to `TODO.md` (project root)
- ❌ NEVER use `# TODO:` in code comments
- ❌ NEVER put TODOs in commit messages

### 8. Temporary Files

**Always use `./.tmp/`:**
- ✅ `./.tmp/` (project root, gitignored)
- ❌ NOT `/tmp`, `~/tmp`, or `/var/tmp`

### 9. Bash Command Execution

**See `ci/docs/standards/ai/CODE-ASSISTANT-COMMON.md` for complete bash usage guidance to minimize permission prompts.**

Quick summary:
- ❌ Avoid: `&&`, `||`, `;`, `|` (triggers permission prompts)
- ✅ Use: Separate Bash calls, `.tmp/` intermediate files, output redirection (`>`)

## Configuration Cascade

**Environment variables > .env > ci.yaml > defaults.yaml**

**Common env vars:**
- `CI_SKIP_HOOKS=true` - Skip git hook installation
- `CI=true` - Running in CI environment
- `BOOTSTRAP_INSTALL=1` - Enable bootstrap installation
- `CI_MERGE_MODE=overwrite` - Force template values to overwrite existing project values in TOML/JSON merges (default: no-overwrite)

## Quick Reference

**Update ci/ submodule:**
```bash
cd ci && git pull origin main && cd ..
git add ci && git commit -m "chore: update ci submodule"
```

**Contribute to HyperCI:**
1. Work in `ci/` directory (changes tracked in hs-ci repo)
2. Commit to `hypersec-io/hs-ci` repository
3. Update project's ci/ submodule reference

**Troubleshooting:**
- Bootstrap fails: Check `.env` has credentials
- Wrong venv: CI scripts enforce ci-local/.venv (will error)
- Submodule issues: `git submodule update --init --force`

---

**See also:**
- `ci/docs/standards/` - AI assistant guidance and coding standards
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
./ci/run build --nuitka  # Nuitka compiled binary (sets CI_NUITKA=1)
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
- `CI_NUITKA=1` - Enable Nuitka compiled build (use --nuitka flag)

**Nuitka Protection Levels:**
- `NUITKA_PROTECTION=none` - Basic compilation
- `NUITKA_PROTECTION=minimal` - Standalone mode only
- `NUITKA_PROTECTION=data-hiding` - Encrypt strings/names (Commercial)
- `NUITKA_PROTECTION=traceback` - Encrypt stdout/stderr (Commercial)
- `NUITKA_PROTECTION=recommended` - Full protection (default for Commercial)

**Testing:**
- `CI_COVERAGE_SOURCE` - Override coverage source directory
- `CI_VERIFY_PUBLISH=1` - Enable post-publish verification

**Release Flags:**
- `--force` - Bypass checks (sets CI_FORCE=1)
- `--no-push` - Keep release local (sets CI_NO_PUSH=1)
- `--nuitka-only` - Publish only Nuitka wheels (sets CI_NUITKA_ONLY=1)

### Python Module Scripts

**Bootstrap Scripts** (`ci/modules/python/bootstrap.d/`):
- `30-python-project.py` - Validate Python project structure
- `31-python-structure.py` - Create src/ layout if needed
- `32-jfrog.py` - Configure JFrog credentials
- `33-nuitka.py` - Check Nuitka requirements (if enabled)

**Runtime Scripts** (`ci/modules/python/run.d/`):
- `30-python-test.py` - Run pytest with coverage + ruff + mypy
- `31-python-dependency-update.py` - Update uv.lock dependencies
- `50-build.py` - Build standard wheel/sdist
- `51-publish.py` - Publish to JFrog Artifactory
- `52-verify-publish.py` - Verify package exists in JFrog
- `55-build-nuitka.py` - Build Nuitka compiled binary

### Dependencies

**ONE pyproject.toml at project root:**
- Project dependencies in `[project.dependencies]`
- CI tool configs in `[tool.*]` sections
- Lockfile: `uv.lock` (auto-managed by uv)

**Install:**
```bash
uv sync --locked                    # Install all deps (project + CI)
```

**Update:**
```bash
./ci/run dependency-update          # Update project deps (uv lock)
```

**CI dependencies auto-installed by bootstrap:**
Bootstrap ensures dynaconf, pyyaml, tomli, tomli-w, and python-semantic-release
are installed in .venv before running CI tools.

### Version Management

**Git tag is the single source of truth for version.**

`./ci/run release` updates all version files atomically:
- VERSION file (plain format: `2.6.0`)
- pyproject.toml (`version = "2.6.0"`)
- src/<package>/__init__.py (`__version__ = "2.6.0"`)
- Creates git tag (e.g., `v2.6.0`)
- All synced in one commit

**Workflow:**
```bash
# Release: Updates VERSION + creates commit + tag
./ci/run release --dry-run   # Preview next version
./ci/run release             # Create and push release (default)
./ci/run release --no-push   # Create release locally (don't push)
./ci/run release --nuitka-only  # Nuitka wheels only (no source)

# Build: Just builds package (doesn't touch VERSION)
./ci/run build              # Standard wheel + sdist
./ci/run build --nuitka     # Nuitka compiled (sets CI_NUITKA=1)
```

**Implementation:**
- semantic-release updates pyproject.toml and __init__.py
- `build_command` runs write-version.py to create plain VERSION file
- All files committed together before tag creation

### GitHub Actions Integration

**Automatic builds** on version tag push (`v*`):
- Standard Python wheel published to JFrog
- Nuitka multi-arch builds (if `nuitka.enabled: true` in ci.yaml)
- Cost-optimized runners (BuildJet, Cirrus)

**Workflow:** `.github/workflows/jfrog-publish.yml`

## Python Code Style Standards

**For both human and AI code assistants:**

### Clarity Over Cleverness
- Break down compound operations into clear steps
- Use intermediate variables with descriptive names
- Prioritize readability over clever one-liners
- Add comments explaining WHY, not just WHAT
- Avoid dense lambda chains and nested comprehensions

### Examples

**❌ Bad (dense, hard to follow):**
```python
result = [x for sublist in [[y**2 for y in range(n) if y % 2] for n in data] for x in sublist if x > 10]
```

**✅ Good (clear, maintainable):**
```python
# Filter data and square odd numbers above threshold
result = []
for n in data:
    odd_numbers = [y for y in range(n) if y % 2]
    squared = [y**2 for y in odd_numbers]
    result.extend([x for x in squared if x > 10])
```

**❌ Bad (unexplained logic):**
```python
if (a and b) or (c and not d):
    process()
```

**✅ Good (explained logic):**
```python
# Process if: (both conditions met) OR (special case without override)
both_conditions_met = a and b
special_case_without_override = c and not d
if both_conditions_met or special_case_without_override:
    process()
```

---

**See also:** `ci/docs/PYTHON.md`, `ci/docs/NUITKA.md`, `ci/docs/TESTING.md`
