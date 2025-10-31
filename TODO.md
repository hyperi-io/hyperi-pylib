# Hyperlib TODO

## Active ⭐

### Security Fixes Published - v2.3.6 ✅

**Status:** COMPLETE - Published and verified in JFrog

**Version:** 2.3.6
**Published:** 2025-10-31
**Artifacts:**
- hyperlib-2.3.6-py3-none-any.whl (48.6 KB)
- hyperlib-2.3.6.tar.gz (47.1 KB)

**Security improvements:**
- ✅ All Medium severity issues resolved (B104, B108)
- ✅ Low severity documented with nosec comments
- ✅ Added tempfile import to runtime.py
- ✅ Removed unused imports
- ✅ All 136 tests passing

**Verified:**
- ✅ Published to JFrog PyPI (hypersec-pypi-local)
- ✅ Installable from JFrog: `pip install hyperlib==2.3.6`
- ✅ Import working: `import hyperlib; hyperlib.__version__`

### Fast Test Mode Implemented - v2.4.0-v2.4.2

**Status:** Implemented in v2.4.0, not yet in JFrog

**Configuration:** [ci-local/ci.yaml:15](ci-local/ci.yaml:15)
```yaml
tests:
  pytest_args: "-m 'not integration'"
```

**Environment override:**
```bash
CI_PYTEST_ARGS="" ./ci/run check  # Run all tests
```

**Performance:**
- Fast mode: 121 tests in ~2s (skips 15 integration tests)
- Full mode: 136 tests in ~3min (all tests)

**Versions:**
- v2.4.0: Fast test mode added
- v2.4.1: GitHub Actions workflow fixes
- v2.4.2: CI script path fixes

**Next:** Publish v2.4.3+ to JFrog via GitHub Actions (currently blocked on debugging)

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

### Refactor Application.mcp() to Use FastMCP

**Priority:** MEDIUM

**Current:** Custom MCP implementation (JSON-RPC over stdio/HTTP)
**Target:** Use FastMCP library for better standards compliance

**FastMCP benefits:**
- Official MCP SDK with full protocol support
- Better error handling and validation
- Automatic capability negotiation
- Type-safe tool/resource/prompt definitions
- Active maintenance and updates

**Migration:**
- Replace custom JSON-RPC handling with FastMCP
- Keep same decorator API (@app.tool, @app.resource, @app.prompt)
- Maintain hyperlib logger + config integration
- Test stdio and HTTP transports

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

**Use cases in hyperlib:**
- Merge config files (base.yaml + override.yaml)
- Merge secrets from multiple sources
- Merge deployment configs (dev.yaml + prod.yaml)

**Benefits:**
- Reusable config merge logic
- Consistent with CI patterns
- Type-safe, well-tested

**Implementation:**
- Create `src/hyperlib/config/merge.py`
- Port functions from ci/modules/common/ci_lib.py
- Add to hyperlib.config exports
- Document in PYTHON-STANDARDS.md

**Dependencies:** Add tomli-w to hyperlib runtime deps (not just dev)

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
