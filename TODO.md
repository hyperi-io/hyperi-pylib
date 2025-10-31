# Hyperlib TODO

## Active ⭐

### ONE .venv Migration - COMPLETE ✅

**Status:** COMPLETE - Deployed to production (v2.4.4)

**Achievements:**
- ✅ Unified .venv at project root (runtime + CI tools)
- ✅ Unified .env at project root (project + CI secrets)
- ✅ Removed ci-local/.venv, ci-local/pyproject.toml, ci-local/uv.lock
- ✅ Updated 35+ files in HyperCI submodule
- ✅ Standard builds work in GitHub Actions
- ✅ Published hyperlib-2.4.4 to JFrog (standard wheel)

**HyperCI commits:** 4 commits (feat, 3 fixes)
**Hyperlib commits:** 3 commits (fix, 2 chore updates)

---

### Fix Nuitka Builds - IN PROGRESS 🔧

**Priority:** HIGH (Nuitka builds completely broken)

**Status:** Currently broken - produces NO .so files, only source

**Issues Found:**
1. ✅ FIXED: Missing `nuitka_protection()` function in ci_lib
2. ✅ FIXED: `get_build_config()` reads wrong location (deleted function)
3. ✅ FIXED: `build_type()` doesn't check BUILD_PROFILE (added fallback)
4. ✅ FIXED: `--script` mode passes wrong action (run.py bug)
5. ❌ TO FIX: Nuitka-commercial installation fails (pip can't find package)
6. ❌ TO FIX: Nuitka builds return success but don't run (silent skip)
7. ❌ TO FIX: Need explicit --index-url for Nuitka install (uv doesn't use pip.conf)

**Current Blocker:**
- `pip install nuitka-commercial` fails even though package exists in JFrog
- Reason: pip.conf not being used by uv-created venv
- Solution: Use explicit `--index-url` in install command

**Acceptance Criteria:**

**Local Nuitka Build (`BUILD_PROFILE=nuitka ./ci/run build`):**
- ✅ Must create .whl with .so files (compiled for local CPU arch only)
- ✅ Must NOT contain .py source files
- ✅ Wheel naming: `hyperlib-X.Y.Z-cp3XX-cp3XX-linux_x86_64.whl` (platform-specific)
- ✅ Contents: `hyperlib/*.so` files (compiled modules)

**GitHub Actions Nuitka Release:**
- ✅ Must create wheels for BOTH x64 AND arm64 architectures
- ✅ Each wheel contains .so files for its specific architecture
- ✅ Must NOT contain .py source files
- ✅ Published to JFrog with both:
  - `hyperlib-X.Y.Z-cp3XX-cp3XX-linux_x86_64.whl` (x64)
  - `hyperlib-X.Y.Z-cp3XX-cp3XX-linux_aarch64.whl` (arm64)
- ✅ Both wheels + tar.gz published automatically (no manual intervention)

**Next Steps:**
1. ✅ FIXED: Nuitka-commercial installation (use token auth)
2. Test locally: BUILD_PROFILE=nuitka ./ci/run build
3. Verify .so files in dist/ wheel
4. Commit and push fixes
5. Test in GitHub Actions: nuitka-x64, nuitka-arm64 builds
6. Verify both architecture wheels in JFrog with .so files

---

## Backlog

### Clean Up ci_lib.py (REFACTOR)

**Priority:** MEDIUM (technical debt)

**Issues:**
1. Inconsistent naming: Some functions have `get_` prefix, others don't
   - ✅ `get_project_root()` - has prefix
   - ❌ `artifactory_username()` - missing prefix
   - ❌ `github_repo_full()` - missing prefix
   - ❌ `package_name()` - missing prefix

2. Duplicate/deprecated code removed:
   - ✅ `get_build_config()` - DELETED (broken, replaced by get_ci_config)

**Proposed:**
- Rename accessor functions for consistency:
  - `artifactory_username()` → `get_artifactory_username()`
  - `artifactory_password()` → `get_artifactory_password()`
  - `package_name()` → `get_package_name()`
  - etc.
- Keep old names as deprecated aliases temporarily
- Update all call sites across HyperCI
- Document naming convention

**Effort:** 20-30 files, 1-2 hours

---

### Test Nuitka with App vs Package Builds

**Priority:** HIGH (after Nuitka fixes)

**Challenge:** Hyperlib is a package (library), not an app
- Package mode: Creates .whl with .so files
- App mode: Creates standalone binary

**Testing Strategy:**
1. **Package mode (hyperlib):** Test in hyperlib directly
   - Current project type, don't break it
   - Should create .whl with .so files

2. **App mode:** Create separate test project
   - Option A: Create minimal test app in `.tmp/test-app/`
   - Option B: Use existing app project (if available)
   - Should create standalone .bin file

**Requirements:**
- Don't modify hyperlib's build type (keep as package)
- Test both modes end-to-end
- Verify artifacts are correct (.so vs .bin)

---

### Refactor Application.mcp() to Use FastMCP

**Priority:** MEDIUM

**Current:** Custom MCP implementation (JSON-RPC over stdio/HTTP)
**Target:** Use FastMCP library for better standards compliance

**File:** `src/hyperlib/application/mcp.py`

---

### Add Config Merge to Hyperlib

**Priority:** MEDIUM

**Current:** CI has sophisticated merge functions in ci_lib.py
**Target:** Port clean merge capability to hyperlib.config

**What to port from ci_lib.py:**
- `deep_merge_json()` - Deep merge dicts/JSON
- `merge_file()` - Auto-detect and merge JSON/YAML/TOML
- TOML merge support (tomllib + tomli-w)

**Dependencies:** Add tomli-w to hyperlib runtime deps

---

## Done ✓

### 2025-10-31 Session - ONE .venv Migration

**ONE .venv Migration:**
- ✓ Updated 35+ files in HyperCI submodule
- ✓ Migrated hyperlib to unified .venv
- ✓ Tested bootstrap, AI, build - all working
- ✓ Published v2.4.4 to JFrog (standard wheel)
- ✓ GitHub Actions → JFrog workflow verified

**HyperCI Improvements:**
- ✓ Removed broken `get_build_config()` function
- ✓ Fixed `build_type()` to check BUILD_PROFILE
- ✓ Fixed `--script` mode bug in run.py
- ✓ Added missing `nuitka_protection()` function
- ✓ Updated all documentation for ONE .venv

**Commits:** 7 total (4 HyperCI, 3 hyperlib)

---

### 2025-10-31 Earlier Session

**Application.mcp() - 5th Deployment Type:**
- ✓ MCPApplication factory implemented
- ✓ Tool/resource/prompt decorators
- ✓ stdio and HTTP transports
- ✓ Pre-wired with hyperlib logger + config
- ✓ Included in v2.3.5

**Security Hardening:**
- ✓ ALL /tmp replaced with tempfile.gettempdir()
- ✓ B108 warnings: 0 (was 21)
- ✓ Temp file policy documented (research-based)
- ✓ PYTHON-STANDARDS.md created

**HyperCI v0.3.2:**
- ✓ Dynamic MCP detection (.mcp.json)
- ✓ TOML merge support (tomllib + tomli-w)
- ✓ Temp file policy in CODE-ASSISTANT templates

---

**Last Updated:** 2025-10-31
