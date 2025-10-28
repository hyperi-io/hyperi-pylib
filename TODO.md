# Hyperlib TODO

## Active ⭐

### Helm Test Failures - Container Registry Authentication

**Status:** IN PROGRESS (blocked on imagePullSecret configuration)

**Problem:**
- 4 Helm tests failing with "context deadline exceeded"
- Artifactory login fails with "Bad Credentials" inside tests
- imagePullSecrets created but pods not using them
- Manual `docker login hypersec.jfrog.io` works fine

**Investigation needed tomorrow:**
1. Check if imagePullSecrets specified in Helm chart pod templates
2. Verify secret name matches ("registry-secret")
3. Test if pods can pull from Artifactory with secret
4. Alternative: Skip Helm tests or use public images only

**Files:**
- tests/integration/test_container_deployment.py (test fixtures)
- src/hyperlib/harness.py (container_registry_login)
- tests/conftest.py (.env loading)
- .env (ARTIFACTORY_CONTAINER_URL config)

**Last test result:** 132 passed, 4 failed (Helm tests), 52 skipped

---

## Done ✓

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
