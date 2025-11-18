# hs-lib TODO

## Active

(No active tasks)

---

## Backlog

### Test release for test-cli-build on GitHub Actions - **1h**

**Status:** Verify Nuitka builds work on BuildJet runners

**Task:**
- Run ./ci/run release in test-cli-build
- Push release tag to trigger GitHub Actions
- Verify BuildJet builds Nuitka binaries successfully
- Verify multi-platform builds (linux-x64, linux-arm64)
- Check JFrog artifact publication

### Create test-package-build project - **2h**

**Status:** Test Nuitka package builds (not app)

**Task:**
- Create test-package-build project
- Configure build_type: package (not app)
- Test Nuitka package compilation (compiled wheel with .so)
- Verify package mode works vs app mode

### Remove hardcoded Python versions from CI - **1h**

**Status:** Use config cascade for all Python version references

**Task:**
- Find all hardcoded Python versions (3.8-, 3.12, etc.)
- Replace with dynamic detection from pyproject.toml requires-python
- Example: vermin --target=3.8- should use detected version
- Ensure all tools use project's Python version requirement

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

### Linters.checklist + JFrog Enforcement + Logging - **5.5h** ✅

**Completed:** 2025-11-18 (Session 2)

**Implemented:**
- Selective linter execution via linters.checklist config
- Empty checklist = all linters run (backward compatible)
- JFrog private PyPI enforcement (default: secure, JFrog-only)
- security.jfrog_enforce config (default: true)
- Warnings when private PyPI not configured
- Warnings when public PyPI fallback enabled
- Fixed log levels (INFO not ERROR) for missing merge files
- RFC3339 timestamps for bash wrapper logging (bootstrap, run)

**Testing:**
- Verified in test-cli-build
- Split files (30-lint, 35-test) working correctly
- Logging now consistent across all wrappers

**CI Version:** hs-ci v1.10.4

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

**Last Updated:** 2025-11-15
