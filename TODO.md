# Hyperlib TODO

## Active

### ❌ FAILED: 1M Context Window Configuration

**Status:** FAILED - Accepting 200K context window for now

**What was attempted:**
- Tried configuring in settings files (didn't work)
- Attempted environment variables in settings.json (didn't work)
- Tried various model string formats (didn't work)
- Attempted `/model` runtime command (not available/didn't work)

**Result:**
- Still getting 200K context window (not 1M)
- Configuration attempts unsuccessful

**Current plan:**
- Accept 200K context window as working configuration
- Use 200K minimal+RAG strategy for standards loading
- May revisit 1M configuration in future if needed

---

### Container-Native Application Patterns - Phase 4 (Documentation & Examples)

**Priority:** MEDIUM (Phases 1-3 complete, need docs/examples for users)

**Status:** Implementation complete (Phases 1-3), documentation/examples remaining (Phase 4)

**What's Complete:**
- ✅ Three profiles (dev/docker/prod) - [src/hyperlib/application/profiles.py](src/hyperlib/application/profiles.py)
- ✅ All 5 mixins (Profile, Signal, CLI, Health, Metrics) - [src/hyperlib/application/mixins/](src/hyperlib/application/mixins/)
- ✅ Mixin composition in all app types (API, Daemon, MCP, Oneshot, CLI)
- ✅ Prometheus-first metrics with OTEL conversion
- ✅ CLI-first pattern with Typer
- ✅ Tests passing (Daemon/MCP/Oneshot: 100%, API: skipped but functional)

**What's Remaining (Phase 4):**

---

## Phase 4: Documentation & Examples (Remaining Work)

### 4.1 Documentation

**Files to create:**

- `docs/KUBERNETES.md` - k8s + HELM + ArgoCD + KEDA deployment guide (~745 lines)
  - Health probes (liveness, readiness, startup)
  - Services (ClusterIP, LoadBalancer, Headless)
  - ConfigMaps and Secrets
  - Prometheus ServiceMonitor integration
  - KEDA autoscaling (Prometheus, CPU, queue depth triggers)
  - ArgoCD GitOps deployment
  - Multi-environment configuration (dev/staging/prod)
  - Pod Disruption Budgets
  - Troubleshooting guide

- Update `docs/README.md` with container deployment examples

### 4.2 Example Projects

**Create complete working examples:**

1. **examples/api-container/** - FastAPI REST API with k8s deployment
   - Application code with health checks and custom dependency checks
   - Multi-stage Dockerfile with debug utilities (curl, nc, ping)
   - Kubernetes manifests (deployment.yaml, service.yaml)
   - Docker Compose with PostgreSQL, Redis, Prometheus
   - Prometheus configuration
   - Complete README with deployment instructions

2. **examples/daemon-container/** - Background worker daemon
   - Daemon application with 3 scheduled tasks
   - Health checks for database and queue dependencies
   - Multi-stage Dockerfile (non-root user, health check)
   - Kubernetes manifests with proper resource limits
   - Docker Compose setup
   - Prometheus metrics for task execution

### 4.3 HELM Chart Templates

**Create production-ready HELM charts:**

**Files:** `templates/helm/hyperlib-app/`

- `Chart.yaml` - HELM chart metadata
- `values.yaml` - Default values with documentation
- `values-dev.yaml` - Development environment overrides
- `values-staging.yaml` - Staging environment overrides
- `values-prod.yaml` - Production environment overrides
- `README.md` - Installation and configuration guide

**Templates:**

- `deployment.yaml` - Pod spec with health probes, multi-profile support
- `service.yaml` - Service with metrics port
- `serviceaccount.yaml` - RBAC service account
- `ingress.yaml` - Ingress with TLS support
- `hpa.yaml` - Horizontal Pod Autoscaler (mutually exclusive with KEDA)
- `scaledobject.yaml` - KEDA ScaledObject (Prometheus/CPU/queue triggers)
- `servicemonitor.yaml` - Prometheus ServiceMonitor
- `pdb.yaml` - Pod Disruption Budget
- `configmap.yaml` - Application configuration
- `secret.yaml` - Secrets management

**Features:**

- Profile-based configuration (dev/docker/prod)
- Health checks with configurable probe timings
- KEDA autoscaling or HPA (mutually exclusive)
- Prometheus ServiceMonitor integration
- Security best practices (non-root, dropped capabilities)
- Zero-downtime rolling updates (maxUnavailable: 0, maxSurge: 1)
- ArgoCD GitOps ready

### Estimated Effort

- Documentation: **2h** (KUBERNETES.md + updates)
- Example projects: **2h** (api-container + daemon-container)
- HELM charts: **1h** (production-ready templates)

**Total:** **4-8h**

---

## DFE Migration Reference (For Future Use)

### 1. dfe-ui-backend (FastAPI REST API)

**Current Architecture** ([src/app.py](file:///projects/dfe-ui-backend/src/app.py)):
- Custom Pydantic BaseSettings for config
- Uvicorn server startup
- File-based logging (logs/)
- No health checks (missing /health, /ready)
- No metrics instrumentation
- No graceful shutdown handling

**Changes Needed**:
```python
# BEFORE (custom setup)
from fastapi import FastAPI
from .config import Settings

settings = Settings()
app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# AFTER (hyperlib framework)
from hyperlib import Application

app = Application.api(
    name="dfe-ui-backend",
    version="1.0.0",
    profile="prod"  # Auto: health checks, metrics, graceful shutdown
)

@app.endpoint("/users")
async def list_users():
    return {"users": [...]}

# CLI execution (replaces uvicorn.run)
if __name__ == "__main__":
    app.run()  # Or: python -m dfe_ui_backend serve --profile prod
```

**Migration Effort**:
- **Lines to change**: ~30-50 (config setup, server startup, main block)
- **Config migration**: Replace Pydantic Settings with hyperlib.config (7-layer cascade)
- **Dockerfile CMD**: Change to `python -m dfe_ui_backend serve --profile prod`
- **Testing**: Add health endpoint tests, metrics collection tests
- **Estimate**: **1h**

**Benefits Gained**:
- ✅ Health endpoints (/health, /ready) - fixes k8s probe gaps
- ✅ Automatic HTTP metrics (requests_total, duration_seconds)
- ✅ Graceful shutdown (prevents in-flight request loss)
- ✅ JSON logging (production-ready)
- ✅ KEDA-compatible metrics for autoscaling

---

### 2. dfe-hunt-runner (Background Daemon Worker)

**Current Architecture** ([src/daemon.py](file:///projects/dfe-hunt-runner/src/daemon.py)):
- Custom signal handling (SIGTERM/SIGINT)
- Subprocess management for hunt execution
- **Critical bug**: Process orphaning in daemon mode
- YAML config loading
- File-based logging
- No health checks (missing HTTP server for k8s)
- No metrics instrumentation

**Changes Needed**:
```python
# BEFORE (custom daemon)
import signal
import subprocess

class HuntDaemon:
    def __init__(self):
        signal.signal(signal.SIGTERM, self.handle_signal)
        self.running = True

    def run(self):
        while self.running:
            self.process_hunt()  # subprocess.Popen()

# AFTER (hyperlib framework)
from hyperlib import Application

app = Application.daemon(
    name="dfe-hunt-runner",
    version="1.0.0",
    profile="prod"  # Auto: health HTTP server, metrics, signal handling
)

@app.task(interval=60)
async def process_hunt():
    """Process hunts from queue."""
    # Task execution logic
    pass

# CLI execution
if __name__ == "__main__":
    app.run()  # Or: python -m dfe_hunt_runner start --profile prod
```

**Migration Effort**:
- **Lines to change**: ~80-120 (signal handling, subprocess mgmt, main loop)
- **Config migration**: Replace YAML loading with hyperlib.config
- **Subprocess tracking**: Leverage SignalHandlerMixin to fix orphaning bug
- **Health server**: Automatic (separate thread on port 8080)
- **Dockerfile CMD**: Change to `python -m dfe_hunt_runner start --profile prod`
- **Testing**: Critical - test no orphaned processes, health server, metrics
- **Estimate**: **2h** (complex subprocess management)

**Benefits Gained**:
- ✅ **Fixes orphaned process bug** (proper subprocess tracking)
- ✅ Health HTTP server (k8s liveness/readiness probes)
- ✅ Automatic task metrics (execution_total, duration_seconds, queue_depth)
- ✅ Graceful shutdown (waits for tasks to complete, 30s timeout)
- ✅ JSON logging (production-ready)
- ✅ KEDA-compatible metrics for autoscaling

---

### 3. dfe-cli-core (CLI Tools)

**Current Architecture** ([src/cli.py](file:///projects/dfe-cli-core/src/cli.py)):
- Click-based CLI (legacy)
- Custom config loader
- File-based logging
- No metrics (CLI tools don't typically need metrics)

**Changes Needed**:
```python
# BEFORE (Click-based)
import click

@click.group()
def cli():
    """DFE CLI tools."""
    pass

@cli.command()
@click.option("--verbose", is_flag=True)
def sync(verbose):
    """Sync data."""
    print("Syncing...")

# AFTER (hyperlib Typer-based)
from hyperlib import Application

app = Application.cli(
    name="dfe-cli-core",
    version="1.0.0"
)

@app.command()
def sync(verbose: bool = False):
    """Sync data."""
    print("Syncing...")

# CLI execution
if __name__ == "__main__":
    app.run()
```

**Migration Effort**:
- **Lines to change**: ~40-60 (Click → Typer migration)
- **Config migration**: Replace custom config with hyperlib.config
- **Type hints**: Add type hints to all command parameters (Typer requirement)
- **Testing**: Update CLI tests to use Typer's CliRunner
- **Estimate**: **1h**

**Benefits Gained**:
- ✅ Type-driven CLI (better IDE support, autocomplete)
- ✅ Automatic help generation from type hints
- ✅ Better error messages (type validation)
- ✅ Rich terminal output (colors, tables, progress bars)
- ✅ Consistent CLI standard across all HyperSec projects

---

### Migration Summary

| App | Type | Estimate | Critical Bug Fix | Key Benefits |
|-----|------|--------|-----------------|--------------|
| dfe-ui-backend | API | **1h** | No | Health checks, metrics, graceful shutdown |
| dfe-hunt-runner | Daemon | **2h** | **Yes** (orphaning) | Fixes orphaning, health server, metrics |
| dfe-cli-core | CLI | **1h** | No | Type-driven CLI, better UX |

**Total:** **4h**

**Recommended Order**:
1. **dfe-cli-core** (simplest, validates Typer migration pattern)
2. **dfe-ui-backend** (moderate, validates API framework)
3. **dfe-hunt-runner** (complex, highest value - fixes critical bug)

---

## Phase 1: Foundation (Week 1)

### 1.1 Profile System
**File:** `src/hyperlib/application/profiles.py`

```python
PROFILES = {
    "dev": {
        "logging": {"format": "console", "level": "DEBUG", "colors": True},
        "health_check": False,
        "metrics": False,
        "graceful_shutdown": True,
        "reload": True,
    },
    "docker": {
        "logging": {"format": "json", "level": "INFO", "colors": False},
        "health_check": True,
        "health_check_port": 8080,
        "metrics": True,
        "metrics_port": 9090,
        "graceful_shutdown": True,
        "shutdown_timeout": 30,
        "reload": False,
    },
    "prod": {
        # k8s + HELM + ArgoCD + KEDA
        "logging": {"format": "json", "level": "INFO", "colors": False},
        "health_check": True,
        "health_check_port": 8080,
        "readiness_initial_delay": 5,
        "liveness_initial_delay": 30,
        "startup_initial_delay": 0,
        "metrics": True,
        "metrics_port": 9090,
        "graceful_shutdown": True,
        "shutdown_timeout": 30,
        "reload": False,
    },
}
```

**Tests:** Profile loading, merging with overrides

---

### 1.2 Base Mixins
**File:** `src/hyperlib/application/mixins/__init__.py`

#### CLIExecutableMixin
- Typer CLI setup for all app types
- Standard commands: `version`, `config`, `validate`
- Health check command (if health_check enabled)

#### SignalHandlerMixin
- SIGTERM/SIGINT handler registration
- Graceful shutdown with timeout
- Calls `on_shutdown` hooks
- Prevents orphaned processes (fixes Hunt Runner bug)

#### ProfileMixin
- Load profile configuration
- Merge with user overrides
- Apply to application features

**Tests:** Mixin composition, signal handling, shutdown timeout

---

### 1.3 Metrics Integration
**File:** `src/hyperlib/application/mixins/metrics.py`

#### MetricsMixin
- Uses existing `hyperlib.metrics` module
- Starts metrics server on `metrics_port`
- Auto-instruments based on app type
- Prometheus naming by default

#### Prometheus → OTEL Auto-Conversion
**File:** `src/hyperlib/metrics/backends/opentelemetry.py`

```python
PROMETHEUS_TO_OTEL = {
    "http_requests_total": "http.server.request.count",
    "http_request_duration_seconds": "http.server.request.duration",
    "task_execution_total": "task.execution.count",
    "task_queue_depth": "task.queue.depth",
}

LABEL_MAP = {
    "method": "http.method",
    "endpoint": "http.route",
    "status": "http.status_code",
}
```

**Tests:** Prometheus naming, OTEL conversion, label mapping

---

## Phase 2: Application Types (Week 2)

### 2.1 Update APIApplication
**File:** `src/hyperlib/application/api/application.py`

**Changes:**
- Inherit mixins: `CLIExecutableMixin`, `SignalHandlerMixin`, `ProfileMixin`, `HealthCheckMixin`, `MetricsMixin`
- Auto-instrument HTTP metrics (Prometheus format):
  - `http_requests_total{method,endpoint,status}`
  - `http_request_duration_seconds{method,endpoint}`
  - `http_requests_in_progress{method,endpoint}`
- Add health endpoints: `/health`, `/ready`
- Add Typer CLI commands: `serve`, `health-check`, `validate`
- Apply profile settings

**Auto-Instrumentation:**
```python
@app.fastapi.middleware("http")
async def metrics_middleware(request, call_next):
    track_counter("http_requests_total", labels={...})
    track_histogram("http_request_duration_seconds", duration, labels={...})
```

**Tests:** Profile application, metrics collection, health endpoints, CLI commands

---

### 2.2 Update DaemonApplication
**File:** `src/hyperlib/application/daemon/application.py`

**Changes:**
- Inherit mixins: `CLIExecutableMixin`, `SignalHandlerMixin`, `ProfileMixin`, `MetricsMixin`
- Auto-instrument task metrics:
  - `task_execution_total{task,status}`
  - `task_execution_duration_seconds{task}`
  - `task_queue_depth{queue}`
  - `worker_pool_busy{pool}`
- Add health HTTP server (separate thread, port 8080)
- Add Typer CLI commands: `start`, `status`, `stop`
- Fix process orphaning bug (proper child process tracking)
- Apply profile settings

**Tests:** Task metrics, health server, signal handling, no orphaned processes

---

### 2.3 Update MCPApplication
**File:** `src/hyperlib/application/mcp/application.py`

**Changes:**
- Inherit mixins: `CLIExecutableMixin`, `SignalHandlerMixin`, `ProfileMixin`, `MetricsMixin`
- Auto-instrument MCP metrics:
  - `mcp_requests_total{method,transport}`
  - `mcp_request_duration_seconds{method}`
- Add health check to MCP protocol
- Add Typer CLI commands: `serve`, `validate`
- Apply profile settings

**Tests:** MCP metrics, health protocol, CLI commands

---

### 2.4 Update OneshotApplication
**File:** `src/hyperlib/application/oneshot/application.py`

**Changes:**
- Inherit mixins: `CLIExecutableMixin`, `SignalHandlerMixin`, `ProfileMixin`
- Auto-instrument job metrics:
  - `job_execution_total{job,status}`
  - `job_execution_duration_seconds{job}`
  - `job_last_success_timestamp{job}`
- Add Typer CLI commands: `run`, `validate`
- Apply profile settings (minimal - oneshot doesn't need health checks)

**Tests:** Job metrics, CLI commands

---

### 2.5 Update CLIApplication (Already Typer-based)
**File:** `src/hyperlib/application/cli/application.py`

**Changes:**
- Inherit mixins: `SignalHandlerMixin`, `ProfileMixin`
- No metrics by default (CLI tools don't need metrics)
- Apply profile settings (logging only)

**Tests:** Profile application, logging format

---

## Phase 3: Health Checks (Week 3)

### 3.1 HealthCheckMixin
**File:** `src/hyperlib/application/mixins/health.py`

**Features:**
- Add `/health` endpoint (liveness - always 200 if running)
- Add `/ready` endpoint (readiness - checks dependencies)
- Support dependency checks (database, cache, etc.)
- Configurable initial delays (k8s probe timings)

**API for Developers:**
```python
app = Application.api(name="my-api", profile="prod")

@app.health_check
def check_database():
    """Check database connection."""
    return db.ping()  # Return True/False

@app.health_check
def check_cache():
    """Check Redis."""
    return redis.ping()
```

**k8s Integration:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
```

**Tests:** Health endpoints, dependency checks, k8s probe timings

---

## Phase 4: Documentation & Examples (Week 4)

### 4.1 Documentation
**Files:**
- `docs/CONTAINER_DEPLOYMENT.md` - Container deployment guide
- `docs/KUBERNETES.md` - k8s + HELM + ArgoCD + KEDA guide
- `docs/PROFILES.md` - Profile reference
- Update `README.md` with container examples

### 4.2 Example Projects
- `examples/api-container/` - Containerized API with HELM chart
- `examples/daemon-container/` - Containerized daemon with KEDA scaling
- Update existing examples to use profiles

### 4.3 HELM Chart Templates
**Files:** `templates/helm/`
- `deployment.yaml` - Pod spec with health probes
- `service.yaml` - Service with metrics port
- `servicemonitor.yaml` - Prometheus ServiceMonitor
- `scaledobject.yaml` - KEDA ScaledObject
- `values.yaml` - Default values

---

## Success Criteria

1. **Developer Experience:**
   ```python
   app = Application.api(name="my-api", profile="prod")
   # Gets: health checks, metrics, graceful shutdown - zero config
   ```

2. **Container Deployment:**
   ```dockerfile
   CMD ["python", "-m", "my_api", "serve", "--profile", "prod"]
   # Just works in k8s with HELM
   ```

3. **KEDA Scaling:**
   ```yaml
   # HELM chart includes KEDA ScaledObject
   # Metrics auto-exposed in Prometheus format
   # No code changes needed
   ```

4. **Backend Flexibility:**
   ```bash
   export METRICS_BACKEND=opentelemetry
   # Auto-converts Prometheus → OTEL semantic conventions
   ```

5. **Tests:** All application types tested with profiles, metrics, health checks

---

## Estimated Effort

- **Phase 1 (Foundation):** **8h** (profile system, mixins, metrics)
- **Phase 2 (Application Types):** **8h** (5 app types, tests)
- **Phase 3 (Health Checks):** **4h** (health mixin, k8s probes)
- **Phase 4 (Documentation):** **4-8h** (docs, examples, HELM)

**Total:** **24-28h**

---

## Risks & Mitigation

1. **Risk:** Backward compatibility with existing apps
   - **Mitigation:** Default profile is `dev` (minimal changes), opt-in for `prod` features

2. **Risk:** Metrics backend switching complexity
   - **Mitigation:** Prometheus-first approach, OTEL conversion is additive

3. **Risk:** KEDA integration edge cases
   - **Mitigation:** Follow Prometheus naming conventions strictly, test with real KEDA

4. **Risk:** Health check dependency detection
   - **Mitigation:** Start simple (manual registration), expand later if needed

---

## Next Actions

1. Review and approve this plan
2. Create feature branch: `feat/container-native-patterns`
3. Start Phase 1: Profile system + base mixins
4. Iterate with tests after each phase

---

## Release Workflow Architecture

**CRITICAL: Understand the distinction between local and remote workflows:**

### Local Workflow (Build + Test)

```bash
./ci/run check   # Tests, lint, type-check - ALL LOCAL
./ci/run build   # Build package - LOCAL ONLY
```

- Runs in local environment
- Uses local `.venv` and `ci-local/.venv`
- Fast feedback loop for development
- No GitHub Actions involved

### Release Workflow (Versioning Local, Build/Publish Remote)

```bash
./ci/run release   # Run semantic-release locally, push tag
```

**What happens:**

1. **Local (semantic-release):** Version management happens HERE
   - Analyzes commits since last tag
   - Determines next version (2.8.8 → 2.8.9)
   - **Updates VERSION file** (must happen before tag push)
   - **Updates CHANGELOG.md** (must happen before tag push)
   - **Creates git tag** (v2.8.9)
   - **Commits changes** (`chore(release): 2.8.9 [skip ci]`)
   - **Pushes tag + commit** to GitHub

2. **GitHub Actions (triggered by tag push):** Build/test/publish happens HERE
   - Tag push triggers workflow → BuildJet runners
   - Checks out code (already has v2.8.9 in VERSION file)
   - `./ci/bootstrap install` - Sets up CI environment (installs uv, gitleaks, etc.)
   - `./ci/run test` - Tests, lint, type-check (**EXACT SAME** CI code as local)
   - `./ci/run build` - Build package with correct version (**EXACT SAME** CI code as local)
   - Publish to JFrog
   - Create GitHub release

**Key Concept:**

- **Build/check/test:** All LOCAL (fast feedback loop)
- **Release versioning:** LOCAL (semantic-release analyzes commits, updates VERSION/CHANGELOG)
- **Release build/publish:** GITHUB CLOUD SIDE (reproducible, auditable)
- **Same CI code:** GitHub cloud uses the **EXACT SAME** `./ci/run` scripts and code as local
- **Cloud environment prep:** GitHub runners need additional setup (uv, gitleaks CLI, compilers) before running the same CI scripts
- **Chicken-and-egg solution:** VERSION file updated locally BEFORE tag push, so cloud build has correct version

---

## Backlog

### HyperCI Improvements - DISCUSS & PLAN

**Based on principles review (see .tmp/hyperci-principles-review.md)**

#### Short-term

1. **Add `./ci/ai refresh` command** - **2h**
   - Re-syncs .claude/ context files with latest standards
   - Updates CODE-ASSISTANT.md with current HyperCI docs
   - Reduces context switching overhead when standards change

2. **Improve error message consistency** - **4h**
   - Wrapper around tool output with consistent formatting
   - Color-coded severity (red = error, yellow = warning)
   - Actionable fix suggestions for all errors

3. **Document two-venv pattern clearly** - **1h**
   - Add FAQ: "Why two .venv directories?"
   - Explain migration path to single .venv
   - Update all docs to reference single .venv only

#### Medium-term

1. **Complete single .venv migration** - **8h**
   - Remove ci-local/.venv entirely
   - Consolidate all deps into project .venv
   - Update all docs and scripts
   - Reduces cognitive load (no two-venv confusion)

2. **Add `./ci/run fix` command** - **2h**
   - Auto-fix ALL auto-fixable issues (black, isort, ruff --fix)
   - Single command instead of running each tool manually
   - Makes conforming to standards even lighter work

3. **Enhance pre-commit hooks** - **4h**
   - Auto-fix formatting on commit (black, isort)
   - Run ruff --fix automatically
   - Only block if non-fixable errors remain

#### Long-term

1. **Unified error reporter** - **8h**
   - Wrapper that standardizes all tool output
   - Consistent format: `[ERROR] file.py:42 - Description`
   - Grouped by severity (errors first, warnings second)
   - Reduces cognitive load parsing different error formats

2. **AI-assisted auto-fix** - **16h**
   - `./ci/run fix --ai` uses Claude/Copilot to suggest fixes for type errors
   - Presents diffs for review before applying
   - Reduces manual intervention further
   - Test-enforceable standards principle in action

3. **Smart context switching detection** - **4h**
   - Track last project worked on
   - Auto-update STATE.md timestamp on `./ci/run test`
   - Warn if project not touched in > 5 days (context switch overhead)

---

### Add Gitleaks Secret Scanning to HyperCI
**Status:** Design complete, ready to implement
**Estimate:** **2h**

### Reorganize src/hyperlib/ to Subdirectory Structure
**Status:** Planned - match application/ pattern
**Estimate:** **1h**

### Refactor Application.mcp() to Use FastMCP
**Status:** Backlog - use library instead of custom implementation

### Clean Up ci_lib.py Naming
**Status:** Backlog - inconsistent `get_` prefixes

---

**Last Updated:** 2025-11-10
