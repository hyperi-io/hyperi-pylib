# TODO - Hyperlib CI Infrastructure Refactoring

Last Updated: 2025-10-10

## Current Sprint: Pure Python CI with Full Self-Containment

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

### Phase 6: Testing & Validation
- [ ] Test full release workflow (no JFrog publish)
- [ ] Test with JFROG_PUBLISH=false
- [ ] Test with JFROG_PUBLISH=true (when ready)
- [ ] Verify all commits this session use 'fix:' prefix
- [ ] Document the refactored CI workflow

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
