# Hyperlib TODO

## Active ⭐

### Helm Test Failures - Image Pull Timeouts

**Status:** PARTIALLY RESOLVED (imagePullSecrets added, still timing out)

**Latest build:** 133 passed, 4 failed, 51 skipped (Exit code: 0, artifacts built)

**Problem:**
- 4 Helm tests still failing with "context deadline exceeded"
- imagePullSecrets NOW in templates (fixed today)
- .env loading working (conftest.py)
- Pods still can't pull images in time (60s timeout)

**Root cause investigation needed:**
1. Check actual pod events for image pull errors (`kubectl get events`)
2. Verify Minikube can pull from Artifactory (test manually)
3. Check if image paths need Artifactory prefix
4. Verify Minikube Docker daemon has credentials

**Options:**
1. Use public images only (no Artifactory auth needed)
2. Pre-pull images into Minikube before tests
3. Skip Helm tests entirely (not core hyperlib functionality)
4. Increase Helm timeout from 60s to 120s

**Files:**
- tests/integration/fixtures/*.txt (7 templates - NOW have imagePullSecrets)
- tests/integration/test_container_deployment.py
- src/hyperlib/harness.py (container_registry_login)

**Today's fixes:**
- ✅ Added imagePullSecrets to all 7 pod/deployment templates
- ✅ Fixed import test (removed sampling)
- ✅ .env loading in conftest.py

---

## Done ✓

### 2025-10-28 Session

**CI Infrastructure (9 commits to hyperci):**
- ✓ CODE-ASSISTANT.md recovered (787 lines) and restructured with ci/ exclusion
- ✓ Commit tag standards (21 tags with validation)
- ✓  consolidation into STATE.md
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

**Documentation:**
- ✓ Hyperlib STATE.md updated with AI override
- ✓ CODE-ASSISTANT.md with LLM token efficiency directives
- ✓ .env.sample simplified (app runtime only)
- ✓ Session summary saved to .tmp/SESSION-2025-10-28.md

---

## Backlog

### Future Enhancements

- Improve Helm test pod template generation (add imagePullSecrets automatically)
- Add pytest-dotenv for cleaner .env loading
- Document Artifactory container registry setup in README
- Add CI log viewer/search tool

---

**Last Updated:** 2025-10-28
