# hs-lib TODO

## Active

### Update Downstream Projects (DFE apps) - **1-2h**

**Status:** hs-lib v2.9.0 released, ready for downstream updates

**Changes needed in each project:**
- Update pyproject.toml: `hyperlib` → `hs-lib`
- Update imports: Keep `from hs_lib` (already correct)
- Update environment variables: `HYPERLIB_*` → `HS_LIB_*`
- Test and verify

**Projects:**
- dfe-ui-backend
- dfe-hunt-runner
- dfe-cli-core

---

## Backlog

### Implement linters vs tests separation in 30-python-test.py - **2h**

**Status:** Config structure ready, implementation needed

**Task:**
- Refactor 30-python-test.py to honor linters.required and tests.required
- Implement linters.fail_fast (stop on first linter failure)
- Implement tests.fail_fast (continue all tests vs stop on first)
- Split run_linters() and run_tests() functions
- Add to defaults.yaml with sensible defaults

**Current:** All checks run unconditionally (linters + tests mixed)
**Goal:** Separate control over linters vs tests

### JFrog Private PyPI Enforcement - **4h**

**Status:** High priority - security improvement

**Task:**
- Implement JFrog private PyPI enforcement with cascade detection
- If JFrog credentials configured and working, FORCE private PyPI only
- If not configured, use public PyPI
- WARN when switching between private and public
- Update all pip/uv install commands to use cascade

### Bootstrap AI --uninstall Command - **1h**

**Status:** Future enhancement

**Task:**
- Add --uninstall flag to ./ci/bootstrap
- Remove AI setup files (.claude/, etc.)
- Clean up AI-related configurations

### Handle No Initial Commit Scenario - **2h**

**Status:** Edge case handling

**Task:**
- Handle repositories with no commits yet
- Graceful fallbacks in git log commands
- Clear error messages when git history needed but missing

---

## Completed (2025-11-18)

### Test Binary Build (Nuitka) - **2h** ✅

**Completed:** 2025-11-18

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

**Last Updated:** 2025-11-15
