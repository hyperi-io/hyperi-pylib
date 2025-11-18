# hs-lib TODO

## Active

### FIX pyproject.toml merge bug - **2h** 🔴 CRITICAL

**Status:** Blocking Nuitka release testing

**Problem:**
- Template dev dependencies (build, twine, PyGithub, requests) not merging
- deep_merge_no_overwrite() works in isolation but not during bootstrap
- Bootstrap shows "Deep merged pyproject.toml" but git diff shows no changes

**Debug steps:**
- Add detailed logging to merge_file() and deep_merge_no_overwrite()
- Check if multiple merges (common + python) overwrite each other
- Verify merge reads/writes correct files
- Test array comparison logic (maybe version specs causing duplicates?)

**Test:** Bootstrap test-cli-build should add 4 new deps to dev array

---

## Backlog

### Complete two-venv reference cleanup - **1h**

**Status:** Partially done, docs still need cleanup

**Task:**
- Fix remaining 12+ files in docs/ with ci-local/.venv references
- Update documentation to reflect unified .venv
- Files: docs/standards/, CONTRIBUTING.md, templates/

### Standardize ci_lib path injection - **2h**

**Status:** User wants simpler pattern (not full walk)

**Task:**
- 37 scripts currently use walk-up pattern for ci_lib
- Create simpler, consistent pattern
- Apply to all scripts uniformly

### Test Nuitka app build release - **1h** (BLOCKED: merge bug)

**Status:** Waiting for pyproject merge fix

**Task:**
- Fix merge bug first (see Active)
- Run ./ci/run release in test-cli-build
- Verify GitHub Actions + BuildJet builds
- Check JFrog artifact publication with jf/gh CLIs

### Create test-package-build project - **2h** (BLOCKED: merge bug)

**Status:** Needs merge fix first

**Task:**
- Create under hypersec-io org (private repo)
- Configure build_type: package (not app)
- Test Nuitka package mode
- Verify compiled wheels (.so files)

### Document CI directory structure and naming conventions - **0.5h**

**Status:** Clarify architecture and naming patterns

**Task:**
- Document why we have ci/modules/python/tools vs hs-lib package
- Explain .d directory pattern (bootstrap.d, run.d)
- Clarify naming: hs-lib (package), hs-ci (CI system), hyperlib (legacy?)
- Add architecture notes to STATE.md or separate doc

### Clean up deprecated CI directories - **0.5h**

**Status:** Audit and remove unused directories

**Task:**
- Check if ci/modules/python/gitci/ is still used (remove if not)
- Check if ci/modules/python/ai/claude/ is still used (templates now?)
- Audit ci/modules/ for any other deprecated directories
- Remove unused code and consolidate

### Handle No Initial Commit Scenario - **2h**

**Status:** Edge case handling

**Task:**
- Handle repositories with no commits yet
- Graceful fallbacks in git log commands
- Clear error messages when git history needed but missing

---

## Completed (2025-11-18)

### CI Infrastructure Improvements - **8h** ✅

**Completed:** 2025-11-18 (Session 2025-11-18-C)

**Features:**
- Linters.checklist: selective execution, backward compatible
- RFC3339 logging: bash wrappers + Python (all consistent)
- Python version cascade: ENV > .env > ci.yaml > pyproject > 3.12
- JFrog simplified: PRIMARY + fallback (no enforcement)
- Script ordering: CI deps after sync (prevents removal)
- Config cascade: merge mode, all settings use cascade now

**Cleanup:**
- Deprecated directories removed (ai/claude/, ci-pyproject.toml)
- Two-venv references: code files updated (docs pending)
- build_type cascade: removed nuitka.build_type duplication
- Origin remote check: helpful error in semantic-release

**Testing:**
- test-cli-build repo created (hypersec-io, private)
- Bootstrap works end-to-end
- Linting + tests passing

**CI Versions:** v1.10.1 → v1.10.16+ (15 releases)

### Test Binary Build (Nuitka) - **2h** ✅

**Completed:** 2025-11-18 (Session 1)

**Major achievements:**
- Created test-cli-build project for testing
- Implemented --local-build flag for local Nuitka testing
- Fixed nuitka-commercial installation (critical indentation bug)
- Auto-detect entry points (main.py, __main__.py, app.py, cli.py)
- Enforce nuitka-commercial only (no OSS fallback)
- Remove public PyPI fallback (JFrog private only)
- Add build and twine to pyproject.toml template
- Remove all hardcoded "hyperlib" package names
- Add libatomic-static checks (bootstrap + GitHub Actions)
- Rename verify-publish to run after Nuitka builds

**Result:** Nuitka app builds work end-to-end with build_type: app

---

## Backlog (continued)

### Container-Native Patterns - Phase 4 Improvements

**Status:** Phases 1-3 complete, Phase 4 docs exist but need refinement

- Improve KUBERNETES.md examples
- Add more HELM chart variations
- Expand example projects with real-world scenarios

**Note:** Application framework marked as WIP with strong warning (will be refactored/replaced)

---

### HS-CI Improvements

**Based on principles review**

#### Short-term
- Add `./ci/ai refresh` command - **2h**
- Improve error message consistency - **4h**
- Document two-venv pattern clearly - **1h**

#### Medium-term
- Complete single .venv migration - **8h**
- Add `./ci/run fix` command - **2h**
- Enhance pre-commit hooks - **4h**

#### Long-term
- Unified error reporter - **8h**
- AI-assisted auto-fix - **16h**
- Smart context switching detection - **4h**

---

**Last Updated:** 2025-11-18
