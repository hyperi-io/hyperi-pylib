# Hyperlib - Project State

**Repository**: https://github.com/hypersec-io/hyperlib
**Type**: Python package (shared library)
**Purpose**: Enterprise infrastructure for all HyperSec Python projects

**Communication Style**: See [.claude/DEREK.md](.claude/DEREK.md) for Derek's preferred style (professional but relaxed Australian, no LLM fluff)

## Session 2025-11-10 - Container-Native Patterns Implementation

### Phase 1: Foundation - Complete ✅
**Status:** Profile system, mixins, and Prometheus→OTEL conversion implemented

**Commit:** `fb4aa3c` - fix: implement Phase 1 container-native patterns foundation

**Implemented:**
- ✅ Profile system (dev, docker, prod)
- ✅ All 5 base mixins (Profile, Signals, CLI, Health, Metrics)
- ✅ Prometheus→OTEL metric name conversion (30+ mappings)
- ✅ 32/32 tests passing (13 profile + 19 mixin tests)

**Files Created:**
- [src/hyperlib/application/profiles.py](src/hyperlib/application/profiles.py) - Profile definitions and loading
- [src/hyperlib/application/mixins/](src/hyperlib/application/mixins/) - 5 mixins (profile, signals, cli, health, metrics)
- [tests/unit/test_profiles.py](tests/unit/test_profiles.py) - 13 profile tests
- [tests/unit/test_mixins.py](tests/unit/test_mixins.py) - 19 mixin tests

**Type Hint Modernization - Complete ✅**
**Commit:** `23defec` - fix: modernize type hints to Python 3.10+ syntax

- Dict → dict, Optional[X] → X | None (PEP 585, PEP 604)
- Net reduction: 152 lines (475 deletions, 323 insertions)
- No functional changes, purely type annotation cleanup

### Phase 2: Application Types - Complete ✅
**Status:** All 5 application types updated to use mixins

**Commit:** `74e59cc` - fix: comprehensive documentation restructure and application framework updates

**Implemented:**
- ✅ APIApplication - Mixins + health endpoints + metrics middleware + serve CLI
- ✅ DaemonApplication - Mixins + health server + task metrics + start CLI
- ✅ MCPApplication - Mixins + MCP metrics + serve CLI
- ✅ OneshotApplication - Mixins + job metrics + run CLI
- ✅ CLIApplication - Mixins + profile-based logging

**Features Added:**
- Health endpoints (/health for liveness, /ready for readiness)
- Auto-instrumented metrics (http_requests_total, task_execution_duration_seconds, etc.)
- Typer CLI commands (serve, start, run, version, config, validate)
- Profile-based feature enablement (dev/docker/prod)
- Graceful shutdown (SIGTERM/SIGINT handling)

### Phase 3: Enhanced Health Checks - Complete ✅
**Status:** HealthCheckMixin fully implemented with standalone HTTP server

**Commit:** `f0706c6` - fix: implement Phase 3 - enhanced HealthCheckMixin

**Implemented:**
- ✅ Standalone HTTP server for non-HTTP apps (Daemon, MCP, Oneshot)
- ✅ /health endpoint (liveness probe - always 200 if running)
- ✅ /ready endpoint (readiness probe - runs dependency checks)
- ✅ @app.health_check decorator for custom checks
- ✅ Automatic shutdown integration (via SignalHandlerMixin)
- ✅ 9 comprehensive tests (profiles, endpoints, shutdown)

**How it works:**
- HTTP apps (API): Health endpoints added to FastAPI directly
- Non-HTTP apps: Standalone HTTP server in daemon thread (port 8080)
- Dependency checks: Registered via `@app.health_check` decorator
- Kubernetes ready: /health for liveness, /ready for readiness

### Phase 4: Documentation & Examples - In Progress 🔄
**Status:** Core documentation complete, examples and HELM charts pending

**Commit:** `80da16c` - docs: add Phase 4 container deployment and profiles documentation

**Completed:**
- ✅ PROFILES.md - Comprehensive profile reference (dev/docker/prod)
- ✅ CONTAINER_DEPLOYMENT.md - Docker deployment guide
- ✅ Updated APP-API.md and APP-DAEMON.md with health check decorator
- ✅ Multi-stage Dockerfile examples
- ✅ Docker Compose examples
- ✅ Prometheus integration guide

**Pending:**
- ❌ KUBERNETES.md - k8s + HELM + ArgoCD + KEDA guide
- ❌ examples/ directory - Working example projects
- ❌ templates/helm/ - HELM chart templates

**Next Steps:** Complete k8s documentation, create example projects

---

## Session 2025-11-10 (Earlier) - Standards Documentation Restructure

### Coding Standards Documentation Restructure - Complete ✅
**Status:** Comprehensive restructure completed with token efficiency and human readability

**Commit message (when ready):** `docs: reduce coding standards to LLM-friendly token-efficient versions`

**Goal:** Reduce Derek's for-human coding and automation standards documents to LLM-friendly reduced token versions while keeping them human-readable.

**Strategy:**
- Core files: Concise summaries with references (~300-600 lines each, auto-loaded by Claude)
- Details files: Comprehensive guides (~400-800 lines each, human reference)
- Token reduction target: 35-50k → 25k tokens (30-50% savings)

**Completed:**

1. **Created standards directory structure** (details/, python/details/, ai-platforms/)

2. **Extracted detailed guides to separate files:**
   - details/DESIGN-PRINCIPLES.md (~420 lines) - SOLID, DRY, KISS, YAGNI
   - details/ERROR-HANDLING.md (~580 lines) - Security-first error handling
   - details/AI-GUIDELINES.md (~850 lines) - AI code assistant best practices with cognitive load research
   - details/NO-MOCKS-POLICY.md (~650 lines) - Production code policy
   - details/TEST-FIRST-DEVELOPMENT.md (~450 lines) - Test-first strategy for existing code
   - python/details/PEP8-GUIDE.md (~600 lines) - Comprehensive PEP 8 guide
   - python/details/HYPERCI-INTEGRATION.md (~800 lines) - Complete HyperCI tooling guide

3. **Condensed core standards files:**
   - CODING-STANDARDS.md: 873 → 561 lines (35% reduction)
   - CODING-STANDARDS-PYTHON.md: 1,151 → 683 lines (41% reduction)
   - GIT-WORKFLOW.md: Added ~500-line "Human-Style Git Commits" section

4. **Created new core standards:**
   - QUICK-REFERENCE.md (~300 lines) - One-page cheat sheet
   - CONTAINERIZATION.md (~600 lines) - Kubernetes + HELM + ArgoCD deployment patterns
   - README.md - Human navigation index with topic/role-based organization

5. **Enhanced AI-GUIDELINES.md with cognitive load research:**
   - Added "Core Principle: Human-First Design" section (cognitive load must be same or less than human-only projects)
   - Included Cognitive Load Theory (Sweller, 1988) - working memory limits
   - Added Derek's bias note: Use "research indicates" not "research shows" for psychology research
   - Comprehensive accessible references (no paywalls):
     - Academic papers: ResearchGate links (Scalabrino et al., 2018)
     - Video: John Sweller keynote (43min, researchED Melbourne 2017)
     - Articles: Florian Krämer (2024), Rustam Zakirullin GitHub doc (2025), DabApps (2024)
   - Explained intrinsic/extraneous/germane cognitive load
   - Linked AI verbosity to extraneous cognitive load

6. **Added new topics to standards:**
   - Test-first development for existing code (TEST-FIRST-DEVELOPMENT.md)
   - AI rabbit-holing prevention strategies (AI-GUIDELINES.md)
   - Human-style git commits (GIT-WORKFLOW.md)
   - Containerization with debug utilities policy (CONTAINERIZATION.md)

**Token Reduction Results:**
- Core auto-loaded files: ~2,900 lines (added CONTAINERIZATION.md, GIT-WORKFLOW expansion)
- Original core files: ~3,060 lines (before restructure)
- Detail files extracted: ~4,350 lines (now on-demand only)
- **Net token savings: ~30% (detail files no longer auto-loaded)**
- Estimated session token usage: ~28k for core standards (down from ~40k)

**Key Design Decisions:**

1. **Human-First Design Principle** (CRITICAL):
   - AI-assisted projects must be indistinguishable from human-only projects
   - Cognitive load must be the same or less than human-written code
   - No AI conventions, patterns, or verbosity that require "translation"
   - Git commits, code style, and documentation follow human patterns

2. **Containerization Standards:**
   - k8s + HELM + ArgoCD deployment pattern
   - Derek's debug utilities policy: Include small utilities (curl, nc, ping) in containers
     - 2-5% image size increase is acceptable for debuggability
     - Removing tiny debug utilities for disk savings is not efficient cost optimization
   - Multi-stage Dockerfiles (separate build/runtime)
   - Health check endpoints required: /health/live, /health/ready, /health/startup
   - Non-root user always

3. **Cognitive Load Research Integration:**
   - Changed "research shows" → "research indicates" (Derek's psychology bias)
   - All references accessible without paywalls
   - Video content included for different learning styles
   - Practical implications explained (intrinsic/extraneous/germane load)

4. **Three Core Principles Integration:**
   - Added core principles section to all major documentation
   - **Principle 1:** Reduce cognitive load (for developers AND AI workflows)
   - **Principle 2:** Reduce context switching overhead (consistent patterns, standardized infrastructure)
   - **Principle 3:** Automated standards enforcement (make conforming light work)
   - These principles now appear in: README.md, CODING-STANDARDS.md, HYPERCI-INTEGRATION.md
   - Context switching guidance added to AI-GUIDELINES.md (23-45min recovery time, $50k/year cost)
   - **Test-enforceable standards design principle** added to AI-GUIDELINES.md:
     - Makes AI assistants more reliable and efficient
     - Automated testing catches AI errors before production
     - Clear success criteria for AI (formatting, types, security, coverage)
     - Enables faster iteration with immediate feedback

5. **HyperCI Principles Review:**
   - Reviewed bootstrap, run, and ai commands against core principles
   - Overall score: 9/10 - excellent implementation
   - Recommendations documented in `.tmp/hyperci-principles-review.md`
   - Short-term: Add `./ci/ai refresh` command, improve error consistency
   - Medium-term: Complete single .venv migration, add `./ci/run fix` command
   - Long-term: Unified error reporter, AI-assisted auto-fix

**Files Modified:**
- ci/docs/standards/CODING-STANDARDS.md (condensed + core principles)
- ci/docs/standards/CODING-STANDARDS-PYTHON.md (condensed)
- ci/docs/standards/GIT-WORKFLOW.md (added human-style commits section)
- ci/docs/standards/README.md (created index + core principles)
- ci/docs/standards/QUICK-REFERENCE.md (created)
- ci/docs/standards/CONTAINERIZATION.md (created)
- ci/docs/standards/details/AI-GUIDELINES.md (cognitive load + context switching + core principles)
- ci/docs/standards/details/TEST-FIRST-DEVELOPMENT.md (created)
- ci/docs/standards/python/details/HYPERCI-INTEGRATION.md (added core principles)

**Files Created:**
- .tmp/hyperci-principles-review.md - HyperCI analysis against core principles

**HyperCI Improvements Added to TODO.md:**
- Short-term: `./ci/ai refresh` command, error consistency, two-venv docs
- Medium-term: Single .venv migration, `./ci/run fix` command, enhanced pre-commit hooks
- Long-term: Unified error reporter, AI-assisted auto-fix, smart context switching detection
- All improvements aligned with three core principles

**Ready for commit:** All requested work complete, awaiting Derek's approval

## Session 2025-11-07 Continued (Part 5)

### Container-Native Application Patterns - Design Complete ✅
**Status:** Design approved, implementation plan in TODO.md, ready to start Phase 1

**Context:**
- Analyzed 3 DFE projects (dfe-ui-backend, dfe-hunt-runner, dfe-cli-core) for containerization patterns
- Identified critical issues: Hunt Runner orphaning bug, inconsistent health checks, no metrics
- Design documents: `~/hyperlib/containerization_analysis.md`, `~/hyperlib/ANALYSIS_SUMMARY.md`

**Key Design Decisions:**
1. **Three Profiles:** dev (local), docker (CI/CD), prod (k8s+HELM+ArgoCD+KEDA)
   - No kubernetes profile (prod = k8s deployment)
   - Profile-based feature enablement (health checks, metrics, logging format)
2. **Mixin-Based Composition:**
   - ProfileMixin, SignalHandlerMixin, CLIExecutableMixin, HealthCheckMixin, MetricsMixin
   - Reusable across all application types
   - Single responsibility, test independently
3. **Metrics Strategy:** Prometheus-first with auto-OTEL conversion
   - Default: Prometheus naming (`http_requests_total`, `task_execution_duration_seconds`)
   - Auto-convert to OTEL semantic conventions when `METRICS_BACKEND=opentelemetry`
   - Zero code changes to switch backends, KEDA-compatible
4. **CLI-First Pattern:** All apps executed as CLI commands in containers
   - Every app type gets Typer CLI (serve, start, run, health-check, version, config)
   - Container CMD: `python -m myapp serve --profile prod`
5. **Opinionated Defaults:** Production-ready out of the box
   - `Application.api(profile="prod")` → health checks, metrics, graceful shutdown
   - `Application.daemon(profile="prod")` → health HTTP server, task metrics, fixes orphaning bug

**Object Inheritance Hierarchy:**
```
APIApplication(CLIExecutableMixin, SignalHandlerMixin, ProfileMixin, HealthCheckMixin, MetricsMixin)
DaemonApplication(CLIExecutableMixin, SignalHandlerMixin, ProfileMixin, MetricsMixin)
MCPApplication(CLIExecutableMixin, SignalHandlerMixin, ProfileMixin, MetricsMixin)
OneshotApplication(CLIExecutableMixin, SignalHandlerMixin, ProfileMixin)
CLIApplication(SignalHandlerMixin, ProfileMixin)
```

**Migration Assessment (DFE Apps):**
- **dfe-cli-core** (CLI): 3-4 hours - Click→Typer migration, type hints, config
- **dfe-ui-backend** (API): 2-3 hours - Replace custom setup with hyperlib framework
- **dfe-hunt-runner** (Daemon): 4-6 hours - **Fixes critical orphaning bug**, subprocess tracking
- **Total effort:** 10-13 hours (1-2 days)

**Implementation Plan (4 Phases, ~3 weeks):**
- **Phase 1 (Week 1):** Profile system, base mixins, metrics integration with Prometheus→OTEL conversion
- **Phase 2 (Week 2):** Update all 5 application types (API, Daemon, MCP, Oneshot, CLI)
- **Phase 3 (Week 3):** HealthCheckMixin with dependency checks, k8s probe timings
- **Phase 4 (Week 4):** Documentation, examples, HELM chart templates

**Next Actions:**
1. Review TODO.md implementation plan
2. Create feature branch: `feat/container-native-patterns`
3. Start Phase 1: Profile system + base mixins
4. Iterate with tests after each phase

## Session 2025-11-07 Continued (Part 4)

### Gitleaks Secret Scanning (HyperCI) - Complete ✅
- Added Gitleaks integration to HyperCI pre-commit hooks
  - Scans staged files for secrets (API keys, passwords, tokens) before commit
  - Blocks commits if secrets detected
  - Gracefully skips if Gitleaks not installed (no errors)
  - ENV: `CI_SKIP_SECRETS_SCAN=1` to disable scanning
- **Implementation:**
  - Pre-commit hook: Section 3 (secrets scanning)
  - Bootstrap (90-git-hooks.py): Checks Gitleaks, suggests installation, installs .gitleaks.toml
  - Template: `.gitleaks.toml` with HyperSec/JFrog rules, test allowlists
- **Behavior:**
  - Not installed: Warning shown on each commit (install instructions provided)
  - Installed: Scans every commit
  - Secrets found: Blocks commit with clear error + instructions
  - Bypass: `git commit --no-verify` (not recommended)
- **Design:**
  - No .d scripts (inline bash in pre-commit hook)
  - Default config from hyperci (ci/modules/common/templates/.gitleaks.toml)
  - Project overrides in project root (.gitleaks.toml)
  - Future projects get Gitleaks automatically via `./ci/bootstrap --install`

### Metrics Backend Abstraction - Complete ✅
- Added backend-agnostic metrics API
  - Unified interface for Prometheus and OpenTelemetry backends
  - Config-based backend switching: `metrics.backend: prometheus` or `opentelemetry`
  - Zero breaking changes (Prometheus remains default)
  - Automatic fallback to Prometheus if backend unavailable
- **Architecture:**
  - `MetricsManager` - Unified API for all backends
  - `MetricsBackend` - Abstract base class
  - `PrometheusBackend` - Wraps existing PrometheusMetrics
  - `OpenTelemetryBackend` - New OTel implementation
- **OpenTelemetry support:**
  - OTLP mode: Push metrics to collector (default)
  - Prometheus mode: Expose metrics for scraping
  - Optional dependency: `pip install hyperlib[opentelemetry]`
  - Dependencies: opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-otlp, opentelemetry-exporter-prometheus
- **Lifecycle management:**
  - Prometheus: Background thread for process/container metrics collection
  - OpenTelemetry: Periodic exporter pushes metrics automatically
  - Both handle start/stop/update lifecycle
- **Testing:**
  - 18 comprehensive tests (17 passing, 1 skipped without OTel)
  - Tests cover: backend switching, fallback behavior, unified API, lifecycle
- **Usage:**
  ```python
  from hyperlib.metrics import create_metrics

  # Default (Prometheus)
  metrics = create_metrics("myapp")

  # OpenTelemetry
  metrics = create_metrics("myapp", backend="opentelemetry")

  # Same API regardless of backend
  metrics.counter("requests", "Total requests").inc()
  metrics.gauge("queue_size", "Queue depth").set(42)
  metrics.histogram("latency", "Latency").observe(0.123)
  ```

## Session 2025-11-07 Continued (Part 3)

### Two-Tier Sensitive Data Anonymization - Complete ✅
- Integrated Presidio with logger filters (two-tier approach)
  - **Tier 1 (default):** Regex-based `SensitiveDataFilter` (fast, zero deps)
  - **Tier 2 (opt-in):** `PresidioSensitiveDataFilter` (ML-based, better accuracy)
  - Configuration: `logging.masking_level: "simple"` (default) or `"advanced"`
  - Automatic fallback: If Presidio not installed, falls back to regex with warning
- Custom recognizers for cybersecurity patterns (50+ patterns)
  - Research from detect-secrets (Yelp), secrets-patterns-db (mazen160), secret-regex-list (h33tlit)
  - Patterns: AWS (AKIA...), Stripe (sk_live_...), GitHub (ghp_..., github_pat_...), OpenAI (sk-..., sk-proj-...),
    Slack (xoxp-...), JWT, SendGrid, Mailchimp, Twilio, Bearer tokens, database URLs, private keys
  - 3 custom recognizers: PasswordRecognizer, ApiKeyRecognizer, SecretKeyRecognizer
- Comprehensive tests with real-world edge cases
  - 42 anonymizer tests: Config files (.env, YAML, JSON), DFE data exports, streaming, false positives
  - Test data from DLPTest.com, Nightfall datasets (realistic SSNs, credit cards, complex patterns)
  - All 42 tests passing (100%)
- Updated dependencies
  - Added `presidio` extra: `pip install hyperlib[presidio]`
  - Standardized on psycopg3: `psycopg[binary]>=3.1.0` (note: hyperlib doesn't use it directly, just lists for users)
- Architecture clarification
  - **Logger filters:** Runtime log masking (for dfe-cli-core, dfe-ui-backend)
  - **Anonymizer module:** Structured data, config files, streaming (separate concern)
  - **Gitleaks:** Pre-commit Git scanning (separate tool, for hyperci not hyperlib)

### Test Status (Updated)
- Hyperlib unit: 165/165 (100%)
  - Anonymizer: 42/42 (config files, streaming, edge cases)
  - Logger filters: 22/22 (regex + Presidio integration)
  - Database: 11/11 (ClickHouse + regression)
  - Others: 90/90 (config, runtime, logger, etc.)

## Session 2025-11-07 Continued (Part 2)

### ClickHouse Database Support - Complete ✅
- Added ClickHouse to `build_database_url()` in hyperlib.database
  - Default port: 9000 (native protocol)
  - Scheme: `clickhouse://`
  - Follows same pattern as PostgreSQL, MySQL, Redis
- Comprehensive tests: 11 tests (7 ClickHouse + 4 regression)
- All tests passing, backward compatible

### Sensitive Data Masking - Tier 1 Complete ✅
- Implemented automatic sensitive data filter for logs
  - 30+ sensitive field patterns (passwords, tokens, API keys, secrets)
  - Multiple format support: JSON, form data, database URLs, key=value
  - Bearer token detection, database URL password masking
  - Custom field support (class-level and instance-level)
- Integrated with hyperlib logger (automatic, zero-config)
  - Default: ENABLED (masks by default)
  - Configurable: `HYPERLIB_LOGGING__MASK_SENSITIVE_DATA=false`
  - Performance: ~5-10μs per log message (negligible overhead)
- Comprehensive tests: 22/22 passing
- Zero external dependencies (stdlib `re` only)

### Opinionated Anonymizer with Presidio - Complete ✅
- Implemented comprehensive anonymizer package (`hyperlib.anonymizer`)
  - **Presets:** minimal (secrets), standard (default), compliance (HIPAA/GDPR/PCI-DSS)
  - **Strategies:** REPLACE, REDACT, MASK, HASH, ENCRYPT
  - **Presidio integration:** ML-based PII detection (50+ entity types)
  - **Graceful fallback:** Helpful errors if Presidio not installed
- **StreamingAnonymizer** for efficient large-data processing:
  - LRU caching for consistent anonymization
  - Optimized for: ClickHouse queries, Polars DataFrames, Kafka streams, large files
  - DataFrame support: Polars (lazy + eager), Pandas
  - Memory-efficient iterators (millions of rows, GB+ files)
- **Convenience functions:**
  - `anonymize_text()`, `anonymize_dict()`, `scan_for_pii()`
  - `anonymize_config_file()`, `scan_file_for_secrets()` (pre-commit hooks)
- **Installation:** `pip install hyperlib[presidio]` (optional dependency)
- **Use cases:**
  - Large database result sets (millions of rows)
  - Data processing (Polars lazy evaluation)
  - Message queues (Kafka, RabbitMQ)
  - Large files (GB+ logs, JSONL)
  - Config file PII detection

### HyperCI Secret Scanning Strategy - Design Complete ✅
- **Researched & selected tool: Gitleaks** (best for CI/CD pre-commit in 2025)
  - Fast (Golang), simple config, low false positives
  - Beats TruffleHog (too slow), detect-secrets (complex), Presidio (wrong domain)
  - Industry standard for pre-commit secret scanning
- **Multi-layer defense strategy:**
  1. Pre-commit hook (local, immediate feedback)
  2. Pre-receive hook (server, cannot bypass)
  3. CI/CD pipeline (PR checks, auditable)
  4. Periodic full scans (historical leaks)
- **Clear separation:**
  - **Gitleaks:** Pre-commit secret scanning (hyperci)
  - **Presidio:** Runtime PII anonymization (hyperlib)
  - Different tools, different domains
- **Design document:** `.tmp/hyperci-secret-scanning-design.md`
  - Complete implementation guide
  - Code examples, configuration, testing
  - Estimated implementation: 3-4 hours

### Next Phase (Future Sessions)
- Integrate Presidio with logger filters (two-tier approach)
  - Tier 1 (default): Regex-based (fast, zero deps) ✅ Already done
  - Tier 2 (opt-in): Presidio (`hyperlib[presidio]`, better accuracy)
  - Graceful fallback if Presidio not installed
- Add comprehensive tests for anonymizer package
- Optional: Implement Gitleaks integration in hyperci

### Python Standards Documentation - Complete (Earlier Session)
- Added comprehensive "No Mocks or Mock Code Policy" to PYTHON-STANDARDS.md
  - Policy: Production code must be complete, no placeholders/TODOs
  - Examples: Bad (mock) vs Good (real) implementations
  - AI assistant warning signs and enforcement checklist
  - Migration path for existing mock code
- Added "Hyperlib Infrastructure Standards" to PYTHON-STANDARDS.md
  - Concise "What to Use When" reference table
  - Module standards for logging, config, runtime, database, metrics, CLI
  - Quick start examples (Application framework vs individual components)
  - Replaced verbose documentation with "use this for that" approach
- Separated hyperci-specific guidance from general project standards
  - Moved ci_lib logging instructions to STATE.md (hyperci development only)
  - PYTHON-STANDARDS.md now covers all projects using hyperlib
  - Clear distinction: ci_lib (internal) vs hyperlib (standard)

## Session 2025-11-03 Completed

### VERSION Sync & Environment Variable Standardization - Complete
- Fixed VERSION file sync (plain `2.6.2` format, atomic with git tag)
- Standardized ALL env vars to CI_ prefix (8 orphans removed)
- Removed 647 lines of complexity (version sync + redundant publish)
- Added nuitka-only release mode (--nuitka-only flag)
- Released v2.6.1 and v2.6.2 successfully

### Code & Documentation Cleanup - Complete
- Separated build/publish responsibilities (removed 99 duplicate lines)
- Updated all documentation to match code
- Fixed README.md API examples
- Moved write-version.py to CI infrastructure
- Removed .python-version (uv uses pyproject.toml)
- Cleaned up 3 obsolete file references

## Session 2025-10-31 Completed

### ONE .venv Migration - Complete
- Unified .venv at project root (runtime + CI tools)
- Published v2.4.4 to JFrog (standard + Nuitka x64 + ARM64)

### Nuitka Builds - Complete
- Package mode: .whl with .so files (NO .py source)
- App mode: Binary + tarball distribution
- Multi-arch: x64 + ARM64

### uv-Managed Python - Complete
- No system Python dependency
- uv downloads Python automatically
- Works on any OS

### Test Status
- HyperCI unit: 56/56 (100%)
- HyperCI integration: 64/64 (100%), 4 skipped
- Hyperlib unit: 143/143 (100%)
  - Database tests: 11/11 (ClickHouse + regression)
  - Logger filter tests: 22/22 (sensitive data masking)

## Quick Start

```bash
# Install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup
./ci/bootstrap --install

# Test
./ci/run check

# Build
./ci/run build

# Nuitka
./ci/run build --nuitka
```

## Strategic Goal: Replace ci_lib with Hyperlib

**Long-term architecture goal** (when hyperlib is stable):

Replace ci_lib.py functions with hyperlib equivalents to reduce duplication:
- Configuration: ci_lib.get_config_value() → hyperlib.config.get_config()
- Logging: ci_lib logger → hyperlib.logger
- Utilities: Port shared functions to hyperlib

**Current Blocker:**
- Circular dependency risk (hyperlib needs hyperci for CI, hyperci needs hyperlib for utils)
- hyperlib must be stable first

**Strategy:**
1. Stabilize hyperlib (production-ready, well-tested)
2. Port ci_lib functions to hyperlib gradually
3. Update hyperci to import from hyperlib
4. Remove duplicate code from ci_lib.py
5. ci_lib becomes thin wrapper around hyperlib

**When Ready:**
- hyperlib config.py has full 7-layer cascade (DONE - Session 2025-11-04)
- hyperlib.config.get_config() supports additional files (DONE - Session 2025-11-04)
- hyperlib logger.py is production-ready (DONE)
- hyperci pip installs hyperlib from JFrog (published package)
- hyperci imports from hyperlib: `from hyperlib.config import get_config`
- ci_lib becomes thin wrapper (80% reduction possible)

## HyperCI Development Guidelines

### Logging in CI Scripts (hyperci development only)

**When developing CI scripts for hyperci, use ci_lib logger:**
```python
from ci_lib import logger

logger.info("Starting build...")
logger.warning("Tests skipped")
logger.error("Build failed")
```

**Features:**
- Consistent formatting across all CI scripts
- Color output for terminal readability
- Appropriate severity levels (info, warning, error)

**Note:** This is ONLY for hyperci CI script development. Normal projects should use hyperlib.logger instead.

## Next Tasks
- Clean up ci_lib.py naming (get_ prefix inconsistency)
- Test coverage for configuration cascade
- Documentation alignment


---

<!-- HYPERCI_STATE_MD: HYPERCI_STATE_MD: ci/modules/common/templates/STATE.md -->
# HyperCI - Common CI/CD Documentation

**Auto-appended to project STATE.md during AI setup**

## Critical Policies for AI Assistants

**ALWAYS READ ON SESSION START:**
1. This STATE.md file (you're reading it now)
2. `TODO.md` (current tasks and priorities)
3. `ci-local/CODE-ASSISTANT.md` - AI assistant guidance (REQUIRED)
4. **ALL files in `ci/docs/standards/`** (critical standards and policies)
   - `GIT-WORKFLOW.md` - Git conventions (REQUIRED)
   - `CHARS-POLICY.md` - Character restrictions
   - Any other standards files present

**Do not skip reading the standards files. They contain critical project-specific requirements.**

### 1. Commit Message Type Selection (UNDERSTATE, NOT OVERSTATE)

**AI assistants frequently overstate importance. Always err on understatement.**

**Default to `fix:` when uncertain:**
- ✅ `fix:` is almost always correct for bug fixes, improvements, refactors
- ❌ Don't use `feat:` unless it's truly a **NEW VERY SIGNIFICANT and BROAD** feature
- ❌ Don't use `BREAKING CHANGE:` unless it breaks backward compatibility

**Valid commit types:**
- `feat:` - **NEW VERY SIGNIFICANT and BROAD user-facing feature** (minor version bump) - RARELY USE
- `fix:` - **Bug fix, improvement, refactor, cleanup** (patch bump) - DEFAULT CHOICE
- `perf:` - Performance optimization only (patch bump)
- `chore:` - Maintenance, deps, config (no bump)
- `docs:` - Documentation only (no bump)
- `test:` - Tests only (no bump)
- `ci:` - CI configuration (no bump)

**Format:** `<type>: <description>` or `<type>(<scope>): <description>`

**Examples of correct usage:**
```
fix: update CI structure documentation          # NOT feat: (just docs)
fix: add commit message validation              # NOT feat: (internal tool)
fix: improve test coverage                      # NOT feat: (tests)
chore: update ci submodule                      # NOT feat: or fix:
feat: add OAuth authentication for users        # OK - NEW user feature
```

**Why this matters:**
- Semantic versioning depends on correct types
- Over-using `feat:` causes unnecessary minor version bumps
- Projects accumulate false "features" in changelogs
- `fix:` is safer and more accurate for most changes

**Validation:** commit-msg hook enforces format (auto-installed by bootstrap)

### 2. Directory Structure

**Read-only ci/ (git submodule):**
- `ci/` - HyperCI scripts (NEVER modify directly)
- `ci/modules/` - Modular CI scripts organized by language
- `ci/docs/` - Documentation

**Writable ci-local/ (project-specific):**
- `ci-local/.venv/` - CI tools only (pytest, ruff, etc.)
- `ci-local/.env` - Credentials (gitignored)
- `ci-local/pyproject.toml` - CI tool dependencies

**Project workspace:**
- `.venv/` - Project dependencies (development)
- `.tmp/` - Temporary files (ALWAYS use this, not /tmp)

### 3. Virtual Environments

**Two separate venvs - NEVER mix:**
- `ci-local/.venv` - CI tools (for CI scripts ONLY)
- `.venv` - Project dependencies (for development)

**CI scripts must use ci-local/.venv:**
```python
if "ci-local/.venv" not in sys.prefix:
    sys.exit("ERROR: Must run in ci-local/.venv")
```

### 4. Bootstrap & Workflow

**Bootstrap (first-time setup):**
```bash
./ci/bootstrap --install
```

Creates both venvs, installs dependencies, installs git hooks.

**Run CI checks:**
```bash
./ci/run check       # All checks (tests, lint, type-check)
./ci/run test        # Tests only
./ci/run build       # Build package
```

**Git hooks (auto-installed by bootstrap):**
- `commit-msg` - Validates branch name, message format, removes AI attribution
- Blocks commits if invalid, warns about formatting issues

### 5. CI Script Locations

**New modular structure:**
```
ci/modules/
├── common/
│   ├── bootstrap.d/     # Bootstrap scripts (run during setup)
│   ├── run.d/           # Runtime checks (branch name, etc.)
│   ├── gitci.d/         # Git operations (hooks, etc.)
│   └── templates/       # File templates (.gitignore, etc.)
└── python/
    ├── bootstrap.d/     # Python bootstrap scripts
    └── run.d/           # Python CI checks (test, build, etc.)
```

**Execution:** All CI scripts run via bash wrappers using `.d` pattern
- `ci/bootstrap` orchestrates `bootstrap.d/*.py` scripts
- `ci/run` orchestrates `run.d/*.py` scripts
- `ci/gitci` orchestrates `gitci.d/*.py` scripts

### 6. TODO Management

**Use TODO.md ONLY:**
- Add todos to `TODO.md` (project root)
- NEVER use `# TODO:` in code comments
- NEVER put TODOs in commit messages

### 7. Temporary Files

**Always use `./.tmp/`:**
- Use `./.tmp/` (project root, gitignored)
- NOT `/tmp`, `~/tmp`, or `/var/tmp`

### 8. Bash Command Execution

**See `ci-local/CODE-ASSISTANT.md` for complete bash usage guidance to minimize permission prompts.**

Quick summary:
- Avoid: `&&`, `||`, `;`, `|` (triggers permission prompts)
- Use: Separate Bash calls, `.tmp/` intermediate files, output redirection (`>`)

## Configuration Cascade

**Environment variables > .env > ci.yaml > defaults.yaml**

**Common env vars:**
- `CI_SKIP_HOOKS=true` - Skip git hook installation
- `CI=true` - Running in CI environment
- `BOOTSTRAP_INSTALL=1` - Enable bootstrap installation

## Quick Reference

**Update ci/ submodule:**
```bash
cd ci && git pull origin main && cd ..
git add ci && git commit -m "chore: update ci submodule"
```

**Contribute to HyperCI:**
1. Work in `ci/` directory (changes tracked in hyperci repo)
2. Commit to `hypersec-io/hyperci` repository
3. Update project's ci/ submodule reference

**Troubleshooting:**
- Bootstrap fails: Check `ci-local/.env` has credentials
- Wrong venv: CI scripts enforce ci-local/.venv (will error)
- Submodule issues: `git submodule update --init --force`

---

**See also:**
- `ci-local/CODE-ASSISTANT.md` - AI assistant guidance (common + language-specific)
- `ci/docs/README.md` - Complete documentation
- `ci/docs/standards/GIT-WORKFLOW.md` - Git conventions


---

<!-- HYPERCI_STATE_MD: HYPERCI_STATE_MD: ci/modules/python/templates/STATE.md -->
# HyperCI - Python CI/CD Documentation

**Auto-appended to project STATE.md during AI setup**

## Python CI Workflow (Quick Reference)

### Available Commands

**Testing:**
```bash
./ci/run check           # All checks (test + lint + type-check)
./ci/run test            # Tests only (pytest with coverage)
./ci/run dependency-update  # Update Python dependencies (uv lock)
```

**Building:**
```bash
./ci/run build           # Standard wheel + sdist (via uv build)
./ci/run build --nuitka  # Nuitka compiled binary
```

**Releasing:**
```bash
./ci/run release --dry-run   # Preview next version
./ci/run release             # Create release + push tag (default)
./ci/run release --no-push   # Create release locally (don't push)
```

**Publishing:**
```bash
./ci/run publish         # Build + publish to JFrog (manual, discouraged)
./ci/run verify-publish  # Verify package exists in JFrog
```

### Python-Specific Environment Variables

**Build Control:**
- `CI_NUITKA=1` - Enable Nuitka build (set by --nuitka flag)
- `CI_NUITKA_ONLY=1` - Publish only Nuitka wheels, skip standard (set by --nuitka-only)

**Nuitka Protection Levels:**
- `NUITKA_PROTECTION=none` - Basic compilation
- `NUITKA_PROTECTION=minimal` - Standalone mode only
- `NUITKA_PROTECTION=data-hiding` - Encrypt strings/names (Commercial)
- `NUITKA_PROTECTION=traceback` - Encrypt stdout/stderr (Commercial)
- `NUITKA_PROTECTION=recommended` - Full protection (default for Commercial)

**Testing:**
- `CI_COVERAGE_SOURCE` - Override coverage source directory
- `CI_VERIFY_PUBLISH=1` - Enable post-publish verification

**Release:**
- Use `./ci/run release` (push is default)
- Use `--no-push` flag to keep local (sets CI_NO_PUSH=1)
- Use `--force` flag to bypass checks (sets CI_FORCE=1)

### Python Module Scripts

**Bootstrap Scripts** (`ci/modules/python/bootstrap.d/`):
- `30-python-project.py` - Validate Python project structure
- `31-python-structure.py` - Create src/ layout if needed
- `32-jfrog.py` - Configure JFrog credentials
- `33-nuitka.py` - Check Nuitka requirements (if enabled)

**Runtime Scripts** (`ci/modules/python/run.d/`):
- `30-python-test.py` - Run pytest with coverage + ruff + mypy
- `31-python-dependency-update.py` - Update uv.lock dependencies
- `49-check-version-sync.py` - Check VERSION sync before release
- `50-build.py` - Build standard wheel/sdist
- `51-publish.py` - Publish to JFrog Artifactory
- `52-verify-publish.py` - Verify package exists in JFrog
- `55-build-nuitka.py` - Build Nuitka compiled binary
- `59-python-version-sync.py` - Sync VERSION across all files

### Dependencies

**Project deps:** `pyproject.toml` + `uv.lock` (project root)
**CI tool deps:** `ci-local/pyproject.toml` + `ci-local/uv.lock`

**Install:**
```bash
uv sync --locked                    # Install project deps
cd ci-local && uv sync --locked     # Install CI tools
```

**Update:**
```bash
./ci/run dependency-update          # Update project deps (uv lock)
cd ci-local && uv lock --upgrade    # Update CI tools
```

### Version Management

**VERSION file is auto-synced** by pre-commit hook (prevents corruption):
- Prevents `{version}` template corruption during semantic-release
- Dual protection: pre-commit hook + CI script (89-version-pre-sync.py)
- Synced across: VERSION, pyproject.toml, src/<package>/__init__.py

**Check sync:**
```bash
./ci/run check-version-sync
```

### GitHub Actions Integration

**Automatic builds** on version tag push (`v*`):
- Standard Python wheel published to JFrog
- Nuitka multi-arch builds (if `nuitka.enabled: true` in ci.yaml)
- Cost-optimized runners (BuildJet, Cirrus)

**Workflow:** `.github/workflows/jfrog-publish.yml`

---

**See also:** `ci/docs/PYTHON.md`, `ci/docs/NUITKA.md`, `ci/docs/TESTING.md`
