# Hyperlib TODO

## Active

### Container-Native Application Patterns - APPROVED DESIGN

**Priority:** HIGH (critical for production deployments)

**Status:** Design approved, ready to implement

**Analysis Documents:** `~/hyperlib/` (containerization_analysis.md, ANALYSIS_SUMMARY.md)

---

## Implementation Plan

### Design Decisions (APPROVED)

1. **Three Profiles:** `dev`, `docker`, `prod` (no kubernetes profile)
   - `dev`: Local development (console logs, no metrics, hot reload)
   - `docker`: Integration testing, CI/CD (JSON logs, metrics, health checks)
   - `prod`: Production = k8s + HELM + ArgoCD + KEDA (all features enabled)

2. **Architecture:** Mixin-based composition
   - `CLIExecutableMixin` - Typer CLI for all app types
   - `SignalHandlerMixin` - Graceful shutdown (SIGTERM/SIGINT)
   - `ProfileMixin` - Profile loading and application
   - `HealthCheckMixin` - Health/readiness endpoints
   - `MetricsMixin` - Auto-instrumentation

3. **Metrics Strategy:** Prometheus-first with auto-OTEL conversion
   - Default: Prometheus naming conventions (`http_requests_total`, `task_execution_duration_seconds`)
   - Backend auto-converts to OTEL semantic conventions when `METRICS_BACKEND=opentelemetry`
   - Zero code changes for developers to switch backends
   - KEDA-compatible by default (Prometheus format)

4. **CLI-First Pattern:** All apps executed as CLI commands
   - Every app type gets Typer CLI with standard commands
   - Standard commands: `version`, `config`, `validate`, `health-check`
   - App-specific commands: `serve` (API), `start` (Daemon), etc.

5. **Opinionated Defaults:** Production-ready out of the box
   - `Application.api()` with `profile="prod"` → health checks, metrics, graceful shutdown
   - `Application.daemon()` with `profile="prod"` → process management, health HTTP server
   - Developer just adds their business logic

---

## Object Inheritance Hierarchy

### Mixin Composition Pattern

**Base Mixins** (single responsibility):
```
ProfileMixin           - Profile loading and application
SignalHandlerMixin     - SIGTERM/SIGINT handling with timeout
CLIExecutableMixin     - Typer CLI commands (version, config, validate)
HealthCheckMixin       - /health and /ready endpoints
MetricsMixin           - Auto-instrumentation based on app type
```

**Application Types** (multiple inheritance):
```
APIApplication(
    CLIExecutableMixin,
    SignalHandlerMixin,
    ProfileMixin,
    HealthCheckMixin,
    MetricsMixin
)
├── Typer commands: serve, health-check, validate, version, config
├── HTTP metrics: http_requests_total, http_request_duration_seconds
├── Health endpoints: /health, /ready
└── Graceful shutdown on SIGTERM/SIGINT

DaemonApplication(
    CLIExecutableMixin,
    SignalHandlerMixin,
    ProfileMixin,
    MetricsMixin
)
├── Typer commands: start, status, stop, version, config
├── Task metrics: task_execution_total, task_execution_duration_seconds
├── Health HTTP server (separate thread on port 8080)
└── Fixes process orphaning bug

MCPApplication(
    CLIExecutableMixin,
    SignalHandlerMixin,
    ProfileMixin,
    MetricsMixin
)
├── Typer commands: serve, validate, version, config
├── MCP metrics: mcp_requests_total, mcp_request_duration_seconds
├── Health check in MCP protocol
└── Graceful shutdown

OneshotApplication(
    CLIExecutableMixin,
    SignalHandlerMixin,
    ProfileMixin
)
├── Typer commands: run, validate, version, config
├── Job metrics: job_execution_total, job_execution_duration_seconds
├── No health checks (one-shot execution)
└── Graceful shutdown if interrupted

CLIApplication(
    SignalHandlerMixin,
    ProfileMixin
)
├── Full Typer CLI (user-defined commands)
├── No metrics by default (CLI tools)
├── No health checks
└── Profile-based logging only
```

**Method Resolution Order (MRO)**:
- Python C3 linearization ensures predictable method lookup
- Mixins ordered left-to-right by initialization priority
- Profile loading happens first, then signal handlers, then features

**Rationale**:
- **Composition over inheritance**: Mixins allow à la carte feature selection
- **Single responsibility**: Each mixin does ONE thing well
- **Reusability**: Same mixins across all application types
- **Testability**: Test mixins independently, then composed apps
- **Flexibility**: Easy to add new mixins or application types

---

## Migration Assessment - DFE Apps

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
- **Estimated time**: 2-3 hours

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
- **Estimated time**: 4-6 hours (complex due to subprocess management)

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
- **Estimated time**: 3-4 hours

**Benefits Gained**:
- ✅ Type-driven CLI (better IDE support, autocomplete)
- ✅ Automatic help generation from type hints
- ✅ Better error messages (type validation)
- ✅ Rich terminal output (colors, tables, progress bars)
- ✅ Consistent CLI standard across all HyperSec projects

---

### Migration Summary

| App | Type | Effort | Critical Bug Fix | Key Benefits |
|-----|------|--------|-----------------|--------------|
| dfe-ui-backend | API | 2-3 hrs | No | Health checks, metrics, graceful shutdown |
| dfe-hunt-runner | Daemon | 4-6 hrs | **Yes** (orphaning) | Fixes orphaning, health server, metrics |
| dfe-cli-core | CLI | 3-4 hrs | No | Type-driven CLI, better UX |

**Total Effort**: ~10-13 hours (1-2 days)

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

- **Phase 1 (Foundation):** 3-4 days
- **Phase 2 (Application Types):** 4-5 days
- **Phase 3 (Health Checks):** 2-3 days
- **Phase 4 (Documentation):** 2-3 days

**Total:** ~3 weeks

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

## Backlog

### HyperCI Improvements - DISCUSS & PLAN

**Based on principles review (see .tmp/hyperci-principles-review.md)**

#### Short-term (1-2 weeks)

1. **Add `./ci/ai refresh` command**
   - Re-syncs  context files with latest standards
   - Updates CODE-ASSISTANT.md with current HyperCI docs
   - Reduces context switching overhead when standards change
   - **Effort:** 4-6 hours

2. **Improve error message consistency**
   - Wrapper around tool output with consistent formatting
   - Color-coded severity (red = error, yellow = warning)
   - Actionable fix suggestions for all errors
   - **Effort:** 6-8 hours

3. **Document two-venv pattern clearly**
   - Add FAQ: "Why two .venv directories?"
   - Explain migration path to single .venv
   - Update all docs to reference single .venv only
   - **Effort:** 2-3 hours

#### Medium-term (1-2 months)

1. **Complete single .venv migration**
   - Remove ci-local/.venv entirely
   - Consolidate all deps into project .venv
   - Update all docs and scripts
   - Reduces cognitive load (no two-venv confusion)
   - **Effort:** 1-2 days

2. **Add `./ci/run fix` command**
   - Auto-fix ALL auto-fixable issues (black, isort, ruff --fix)
   - Single command instead of running each tool manually
   - Makes conforming to standards even lighter work
   - **Effort:** 4-6 hours

3. **Enhance pre-commit hooks**
   - Auto-fix formatting on commit (black, isort)
   - Run ruff --fix automatically
   - Only block if non-fixable errors remain
   - **Effort:** 6-8 hours

#### Long-term (3-6 months)

1. **Unified error reporter**
   - Wrapper that standardizes all tool output
   - Consistent format: `[ERROR] file.py:42 - Description`
   - Grouped by severity (errors first, warnings second)
   - Reduces cognitive load parsing different error formats
   - **Effort:** 1-2 weeks

2. **AI-assisted auto-fix**
   - `./ci/run fix --ai` uses/Copilot to suggest fixes for type errors
   - Presents diffs for review before applying
   - Reduces manual intervention further
   - Test-enforceable standards principle in action
   - **Effort:** 2-3 weeks

3. **Smart context switching detection**
   - Track last project worked on
   - Auto-update STATE.md timestamp on `./ci/run test`
   - Warn if project not touched in > 5 days (context switch overhead)
   - **Effort:** 1 week

---

### Add Gitleaks Secret Scanning to HyperCI
**Status:** Design complete, ready to implement
**Effort:** 3-4 hours

### Reorganize src/hyperlib/ to Subdirectory Structure
**Status:** Planned - match application/ pattern
**Effort:** 1-2 hours

### Refactor Application.mcp() to Use FastMCP
**Status:** Backlog - use library instead of custom implementation

### Clean Up ci_lib.py Naming
**Status:** Backlog - inconsistent `get_` prefixes

---

## Completed (Recent)

### 2025-11-07 - Typer Migration & Application Restructure
- Migrated CLIApplication from Click to Typer (mandatory CLI standard)
- Restructured all application types to proper submodule packages
- Tests: 15/15 passing

### 2025-11-04 - Config File Merge Module
- Added comprehensive config file merge to hyperlib.config
- Supports JSON, YAML, TOML, INI, .env, .gitignore
- Auto-detection, deep merge, append strategies
- Tests: 71/71 passing

### 2025-11-04 - Metrics Backend Abstraction
- Added Prometheus and OpenTelemetry support
- Backend detection and graceful fallback
- Tests: 17/18 passing (1 skipped)

### 2025-10-31 - ONE .venv Migration
- Unified .venv at project root (runtime + CI tools)
- Published v2.4.4 to JFrog

### 2025-10-31 - Nuitka Builds
- Fixed all Nuitka build issues
- Multi-arch support (x64 + ARM64)
- Package mode (.whl with .so files)

### 2025-10-31 - Application.mcp()
- 5th deployment type implemented
- stdio and HTTP transports
- Included in v2.3.5

---

**Last Updated:** 2025-11-07
