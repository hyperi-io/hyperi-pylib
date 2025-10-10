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

### Phase 2: Replace Node.js semantic-release with Python (IN PROGRESS)
- ✅ Research python-semantic-release library
- ✅ Install python-semantic-release in ci/.venv
- ✅ Configure in pyproject.toml [tool.semantic_release]
- 🔄 Simplify 90-semantic-release.py to use Python CLI
- [ ] Test Python semantic-release creates clean commits
- [ ] Remove npm semantic-release dependency (if desired)

### Phase 3: Replace subprocess with Native Python
- [ ] Replace JFrog CLI with Python requests/twine (already using twine)
- [ ] Replace GitHub CLI with PyGithub library
- [ ] Replace git commands with GitPython library where possible
- [ ] Audit all subprocess calls in CI scripts
- [ ] Document which subprocess calls remain (if any)

### Phase 4: Simplify Bootstrap
- [ ] Move Python tools installation to pure Python
- [ ] Reduce bash scripts to single Python-check only
- [ ] Make bootstrap 100% Python after Python check
- [ ] Test bootstrap works without bash dependencies

### Phase 5: JFrog Publishing Controls
- [ ] Add JFROG_PUBLISH env var (default: auto-detect from creds)
- [ ] Add --no-publish flag to ./ci/ci release
- [ ] Validate JFrog u/pwd authentication
- [ ] Validate JFrog u/token authentication
- [ ] Document JFrog authentication in STATE.md

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
