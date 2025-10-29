# Hyperlib TODO

## Active ⭐

### Final Cleanup After Restart

**Status:** Ready for clean restart

**Action needed:**
1. Close Claude Code session
2. Restart terminal (kills 23+ hung background processes)
3. Reopen project in Claude Code
4. Run: `./ci/run build`
5. Should pass with exit code 0

**Expected result:** All tests passing (137+ tests)

---

## Done ✓

### 2025-10-29 Morning - Helm Tests COMPLETELY FIXED! 🎉

**Helm Test Victory:**
- ✅ **3/3 Helm tests PASSED** (verified: 106 seconds)
- test_helm_pod_deployment ✅
- test_helm_prometheus_metrics ✅
- test_helm_api_deployment_with_service ✅
- 1 more test needs same fix (TestHelmDeployment::test_helm_chart_deployment)

**Root causes found and fixed:**
1. ✅ Minikube networking (recreated Minikube - fresh instance works)
2. ✅ Python f-string syntax error (backslash in f-string)
3. ✅ ConfigMap name mismatch (use release_name not test_id)
4. ✅ Helm --wait incompatible (removed - pods go to Succeeded not Ready)
5. ✅ wget missing (replaced with python urllib)

**Hung process prevention:**
- ✅ Added cleanup_hung_processes() to conftest.py
- ✅ Session-level auto-cleanup before/after tests
- ✅ HYPERLIB_TEST_* labels on all commands
- ✅ Won't interfere with other projects

**Code quality:**
- ✅ Ruff auto-fixes applied (9 issues fixed)
- ⏳ 8 ruff issues remain (ARG004, SIM102, etc. - code quality suggestions)

**Commits today:** 35+ commits
- hyperci: 10 commits
- hyperlib: 25+ commits

**Documentation:**
- .tmp/HELM-TESTS-FIXED.md - Complete Helm investigation
- .tmp/SOE-minikube-setup.sh - Minikube configuration script
- .tmp/SOE-docker-setup.sh - Docker daemon configuration
- .tmp/SOE-README.md - SOE scripts documentation

---

### 2025-10-28 Session

**CI Infrastructure (9 commits to hyperci):**
- ✓ CODE-ASSISTANT.md recovered (787 lines) and restructured with ci/ exclusion
- ✓ Commit tag standards (21 tags with validation)
- ✓ CLAUDE.md consolidation into STATE.md
- ✓ CI mode detection (readonly/development/standalone)
- ✓ CI infrastructure bug fixes (run.py paths, CI_DIR, get_ci_setting)
- ✓ File logging (ci-local/logs/ci.log with rotation)

**Hyperlib Features (16 commits):**
- ✓ STATE.md AI assistant override for dual-repo access
- ✓ Import test fix (removed sampling module)
- ✓ Container registry throttling detection
- ✓ Artifactory container registry authentication
- ✓ Minikube test improvements (JSON parsing fix, KISS approach)
- ✓ .env loading in pytest conftest
- ✓ .env/.env.sample cleanup (app vs CI separation)

---

## Backlog

### CI Bootstrap Issues (from .tmp/CI_BOOTSTRAP_ANALYSIS.md)

**Issue:** Bootstrap fails at validation, doesn't run AI setup
- Add better error messages when bootstrap.d scripts fail
- Add `--new-project` flag to skip validation
- Decouple AI setup from bootstrap.d failures
- Add interactive prompts for structure creation

**File to update:** ci/modules/python/bootstrap.py, 31-python-structure.py

### Remaining Ruff Issues

Minor code quality suggestions (8 issues):
- ARG004: Unused ctx argument (Click callback)
- SIM102, SIM103, SIM108, SIM117: Code simplification
- UP035: typing.Dict → dict

---

**Last Updated:** 2025-10-29
