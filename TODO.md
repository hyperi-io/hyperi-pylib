# Hyperlib TODO

**Last Updated:** 2025-10-16 (End of HyperCI creation session)

---

## Current Status

**Hyperlib:**
- Using hyperci via git submodule ✅
- Native uv mode working (uv sync, uv build) ✅
- Nuitka compiled wheels working ✅
- 28 commits pushed ✅

**HyperCI (hypersec-io/hyperci):**
- Central CI repository created ✅
- 13 commits pushed ✅
- Production-ready ✅

**Pending:** Minor test script fix (see Priority 1 below)

---

## Priority 1: Fix Test Script ⭐ CRITICAL (Next Session)

**Issue:** Tests can't import hyperlib because of complete venv separation

**Current State:**
- ci/.venv has: pytest, ruff, black, mypy (CI tools only)
- .venv has: dynaconf, loguru, pyyaml (project deps only)
- Tests need: pytest AND project deps (both venvs)

**Solution (Recommended):**

Add pytest to dependency-groups in pyproject.toml:
```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.12.0",
    "black>=25.0.0",
    "isort>=5.12.0",
    "mypy>=1.0.0",
]
```

Then:
```bash
uv lock  # Update uv.lock with dev group
uv sync --group dev  # Install into .venv
.venv/bin/pytest tests/  # Should work now
```

Update test script to use .venv for pytest (has project deps + test tools).

**Files to Modify:**
- pyproject.toml (add dependency-groups.dev)
- uv.lock (regenerate with `uv lock`)
- ci/python/ci.d/20-python-test.py (already updated to use .venv for pytest)

---

## Priority 2: Complete ci/local/ Migration ⚠️

**Change:** `.ci.local/` → `ci/local/` (cleaner, all CI in one place)

**Status:**
- ✅ ci/.gitignore has "local/" (submodule ignores it)
- ⚠️ bootstrap.py still scans `.ci.local/` (needs update)
- ⚠️ ci/run still scans `.ci.local/` (needs update)

**Files to Update:**
- ci/python/bootstrap.py (change paths)
- ci/run (change paths)
- ci/docs/PROJECT-EXTENSIONS.md (update all examples)

**Test:**
```bash
mkdir -p ci/local/python/ci.d
echo '#!/usr/bin/env python3' > ci/local/python/ci.d/95-test.py
chmod +x ci/local/python/ci.d/95-test.py
./ci/run check  # Should find ci/local scripts
```

---

## Priority 3: GitHub Actions Testing

**Blocker:** Requires GH_PAT secret

**Setup Steps:**
1. GitHub Settings → Developer settings → Personal access tokens
2. Create token with `repo` scope
3. Add to hyperlib repo: Settings → Secrets → Actions
   - Name: `GH_PAT`
   - Value: (the PAT)

4. Test: Manual trigger or tag push
   ```bash
   git tag v1.6.1-test
   git push origin v1.6.1-test
   gh run watch
   ```

**Expected:** Workflow accesses private hyperci submodule successfully

---

## Priority 4: CI Tool Locking Strategy (Decision Needed)

**Question:** Should ci/.venv use uv.lock for reproducible CI tools?

**Options:**

**A) ci/local/uv.lock** (Per-project, RECOMMENDED):
- Each project can lock CI tool versions separately
- ci/local/pyproject.toml + ci/local/uv.lock
- Flexibility for projects with different needs

**B) ci/uv.lock** (Shared across all projects):
- One lock file in hyperci repo
- All projects use same CI tool versions
- Simpler, more consistent

**C) No lock** (Current):
- Latest compatible versions
- Simpler, less reproducible

**Recommendation:** Option A (ci/local/uv.lock)
- Gives projects control while maintaining defaults
- Document in ci/docs/README.md

**Implementation:** Add to bootstrap logic

---

## Lower Priority (This Week)

### Nuitka Binary Publishing

**Current:** Publishes wheels to hypersec-pypi-local
**Needed:** Detect build_type and publish to correct repo

**Logic:**
```yaml
if build_type == "package":
    twine upload dist/*.whl → hypersec-pypi-local
elif build_type == "app":
    jf rt upload dist-nuitka/*.bin → hypersec-binaries
```

**File:** .github/workflows/nuitka-release.yml (publish-jfrog job)

---

### DFE Project Pilot

After hyperlib CI fully working:
1. Pilot with dfe-hunt-runner (follow MIGRATE guide)
2. Document lessons learned
3. Iterate on hyperci based on feedback

**Migration guides ready:**
- ci/docs/MIGRATE-dfe-hunt-runner.md ✅
- ci/docs/MIGRATE-dfe-ui-backend.md ✅
- ci/docs/MIGRATE-dfe-cli-core.md ✅ (recommends NOT migrating)

---

## Future Enhancements

### From DFE Projects (see ci/docs/FEATURE-GAP-ANALYSIS.md)

**High Value:**
- Commit-msg version bumping (alternative to semantic-release)
- Auto-commit version bumps (git add, commit, tag, push)
- Docker-based Nuitka builds (cross-compile ARM64 on x64)
- Binary validation/testing (smoke tests)

**Medium Value:**
- Service container documentation (PostgreSQL, ClickHouse)
- Docker deployment patterns

---

## Blocked/Deferred

- None currently

---

## Completed This Session (2025-10-16)

**Major Accomplishments:**
1. Created hypersec-io/hyperci central repository
2. Converted hyperlib to use hyperci submodule
3. Implemented native uv mode (uv sync, uv build)
4. Created extension system (ci/local/)
5. Built Nuitka compiled wheels (556 KB with .so)
6. Published to JFrog successfully
7. Analyzed 3 DFE projects for compatibility
8. Created comprehensive migration guides
9. Fixed GitHub Actions for private submodules
10. Created hypersec-binaries JFrog repository

**Commits:** 40+ total (13 hyperci, 28 hyperlib)
**Duration:** ~10 hours
**Status:** Production-ready pending test script fix

---

## Quick Reference

**Bootstrap:** `./ci/bootstrap --install`
**Test:** `ci/.venv/bin/python ci/python/ci.d/20-python-test.py check` (needs fix)
**Build:** `ci/.venv/bin/python ci/python/ci.d/80-build.py build` ✅ works
**Nuitka:** `ci/.venv/bin/python ci/python/ci.d/85-build-nuitka.py build` ✅ works

**Submodule Update:** `cd ci && git pull origin main && cd .. && git add ci`

**Key Docs:**
- ci/docs/README.md - Complete guide
- ci/docs/SESSION-SUMMARY.md - This session's work
- CLAUDE.md - Project state
