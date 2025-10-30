# Hyperlib TODO

## Active ⭐

### Publish v2.3.5 to JFrog

**Status:** Build created, not published (linting blocks)

**Version:** 2.3.5
**Artifacts:** dist/hyperlib-2.3.5-py3-none-any.whl (48K)
**Includes:** Application.mcp() + security fixes

**Blocking issues:**
- pytest: Some tests may be timing out (Minikube?)
- bandit: 13 remaining (Low severity, non-B108)

**Next steps:**
1. Fix pytest failures (check Minikube)
2. Address remaining bandit warnings
3. Run: `./ci/run build` → publish to JFrog
4. Verify MCP in package with jf cli

---

## Backlog

### ONE .venv Migration (MAJOR REFACTOR)

**Priority:** HIGH (eliminates LLM confusion)

**See:** `.tmp/SESSION-HANDOFF-2025-10-31.md` for complete plan

**Summary:**
- Merge ci-local/.venv into .venv
- Use pyproject.toml optional-dependencies dev group
- Update all CI scripts (.venv/bin/* not ci-local/.venv/bin/*)
- Delete ci-local/.venv, ci-local/pyproject.toml

**Benefits:** No venv confusion, standard Python pattern, LLM-friendly

**Effort:** 20-30 commits, 2-3 hours, thorough testing

---

### Expand PYTHON-STANDARDS.md

**Location:** `ci/docs/standards/PYTHON-STANDARDS.md`

**Current:** Temp file policy only

**Add from project experience:**
- Virtual env patterns, config cascade, logging
- Testing, security, build, release workflows
- Container/Helm deployment patterns
- Application factory pattern

**Add industry best practices:**
- DevOps, DataOps, DevSecOps patterns
- Modern Python (PEPs 517/518/621/751, type hints)
- Async, database, API, observability

**Goal:** Comprehensive Python guide for all HyperSec projects

---

## Done ✓

### 2025-10-31 Session

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

**Total:** 140 commits (76 hyperlib + 64 CI)

---

### 2025-10-29 Morning - Helm Tests COMPLETELY FIXED

**All 136 tests passing:**
- ✓ All 4 Helm tests passing
- ✓ Hung process cleanup working
- ✓ Minikube networking fixed

**Fixes:**
- ✓ ConfigMap name mismatch
- ✓ Helm --wait removed
- ✓ Python f-string syntax
- ✓ wget → python urllib
- ✓ Pod Ready wait added

---

**Last Updated:** 2025-10-31
