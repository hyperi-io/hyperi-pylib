# TODO - Hyperlib CI Infrastructure Refactoring

Last Updated: 2025-10-16

## Current Sprint: Nuitka Multi-Architecture Builds (COMPLETED ✅)

### Phase 0: Full Self-Containment (COMPLETED ✅)
- ✅ Restructured /scripts → /ci directory
- ✅ Moved .venv-ci → ci/.venv (full isolation)
- ✅ Renamed scripts/ci → ci/run (clearer naming)
- ✅ Cleaned up pyproject.toml dev extras (removed CI tools)
- ✅ CI dependencies now in ci/bootstrap.d/20-python-tools.py only
- ✅ Updated all paths across codebase and docs
- ✅ Tested bootstrap and CI work correctly

### Phase 1: Multi-Layer venv Protection (COMPLETED ✅)
- ✅ Implement environment variables in activation scripts
- ✅ Add marker files (.venv/.THIS_IS_DEV_VENV, ci/.venv/.THIS_IS_CI_VENV)
- ✅ Update STATE.md with clear venv usage guidelines for LLMs
- ✅ Create venv validation helper function (ci_lib.py)
- ✅ Document protection strategy (8 layers implemented)

### Phase 2: Replace Node.js semantic-release with Python (COMPLETED ✅)
- ✅ Research python-semantic-release library
- ✅ Install python-semantic-release in ci/.venv
- ✅ Configure in pyproject.toml [tool.semantic_release]
- ✅ Simplify 90-semantic-release.py to use Python CLI (420→199 lines, 53% reduction)
- ✅ Fix duplicate config sections and deprecation warnings
- ✅ Test Python semantic-release dry-run mode (works correctly)
- ✅ VERSION file now written by build_command
- 📝 Node.js semantic-release can be removed (optional - not blocking)

### Phase 3: Consolidate and Document Subprocess Usage (COMPLETED ✅)
- ✅ Audited all subprocess calls across CI scripts
- ✅ Documented subprocess usage policy in ci_lib.py
- ✅ Created ci/SUBPROCESS-USAGE.md comprehensive audit
- ✅ Verified git is system dependency (checked in bootstrap.d/00-check-git.sh)
- ✅ Consolidated git operations into ci_lib.py helpers
- ✅ Decision: Use subprocess for standard tools (git), native Python for libraries
- ✅ Already using native Python: build, twine, semantic-release
- 📝 Avoided wrapper libraries (GitPython, PyGithub) - they use subprocess internally anyway

### Phase 4: Simplify Bootstrap (COMPLETED ✅)
- ✅ Converted all bash scripts to Python
- ✅ Created 00-check-git.py (replaces .sh version)
- ✅ Created 10-check-python.py (replaces .sh version)
- ✅ Created 11-check-uv.py (replaces .sh version)
- ✅ Removed all .sh files from ci/bootstrap.d/
- ✅ Bootstrap now 100% Python after initial venv creation
- ✅ Tested bootstrap works with Python checks ✓
- ✅ Uses shutil.which() for command detection
- ✅ Consistent error messages and return codes

### Phase 5: JFrog Publishing Controls (COMPLETED ✅)
- ✅ Add publish action to 80-build.py with JFrog upload via twine
- ✅ Add JFROG_PUBLISH env var (default: auto-detect from creds)
- ✅ Add --no-publish flag to ./ci/run
- ✅ Implement should_publish_to_jfrog() with 3-way logic
- ✅ Support both token auth (JF_TOKEN) and username/password (JF_USER/JF_PASSWORD)
- ✅ Test JFROG_PUBLISH=false (skips publishing) ✓
- ✅ Test auto-detect mode (finds credentials) ✓
- ✅ Document JFrog authentication and publishing in STATE.md

### Phase 6: Testing & Validation (COMPLETED ✅)
- ✅ Verified all commits this session use 'fix:' prefix (9 commits)
- ✅ Tested semantic-release dry-run with --print flag (shows 2.0.0)
- ✅ Fixed VERSION file template in build_command (use Python instead of echo)
- ✅ Tested JFROG_PUBLISH=false (correctly skips publishing)
- ✅ Tested JFROG_PUBLISH auto-detect (correctly finds credentials)
- ✅ Validated bootstrap with all Python checks (no bash)
- ✅ Validated CI infrastructure is self-contained in /ci directory
- 📝 JFrog publishing tested locally, GitHub Actions for production

### Phase 7: Nuitka Multi-Architecture GitHub Actions (COMPLETED ✅)
- ✅ Analyzed Nuitka workflow issues (mismatch between local and GitHub builds)
- ✅ Fixed GitHub Actions workflow to use setup.py bdist_nuitka (compiled wheels)
- ✅ Updated ARM64 runner configuration to use ubuntu-24.04-arm
- ✅ Documented dual-build strategy in STATE.md:
  - Local builds: Single architecture (x64 or ARM64), fast testing
  - GitHub Actions: Multi-architecture (x64 + ARM64), production distribution
- ✅ Documented multi-arch builds in ci/docs/NUITKA.md
- ✅ Added GitHub Actions ARM64 knowledge base to STATE.md:
  - Web search verified: ARM64 runners FREE for public repos (GA Aug 2025)
  - Documented pricing: $0.02/min for 8-core ARM64 (37% cheaper than x64)
  - Documented runner labels: ubuntu-24.04-arm, ubuntu-22.04-arm
  - Private repos require GitHub Team/Enterprise plan
- ✅ Fixed workflow to properly build compiled wheels (.whl with .so)
- ✅ Updated cost estimates and recommendations

## Completed (Earlier Sessions)
- ✅ Removed 85-deploy.py (local JFrog publishing)
- ✅ Removed sampling.py module
- ✅ Updated CI workflow to GitHub Actions only
- ✅ Fixed bootstrap to be self-contained
- ✅ Added runtime venv checks to CI scripts
- ✅ Enforced ci/.venv in CI runner (removed fallback)
- ✅ Tested semantic-release creates v1.6.0 tag
- ✅ Designed 8-layer venv protection strategy
- ✅ Full CI restructure: /scripts → /ci with full self-containment
- ✅ pyproject.toml cleanup: CI tools separated from project deps

## Deferred
- GitHub Actions JFrog publishing (workflow exists, not testing now)
- Actual JFrog deployment (working on CI infrastructure first)

## Notes
- All commits this session MUST use 'fix:' prefix for patch increments
- Don't publish to JFrog unless explicitly requested
- Focus: CI infrastructure, not hyperlib features
