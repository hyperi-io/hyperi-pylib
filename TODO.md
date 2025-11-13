# Hyperlib TODO

## 🚨 CRITICAL: Package Rename - hyperlib → hs-lib, hyperci → hs-ci

**Status:** Planning complete, ready to execute
**Decision:** `hs-lib` + `hs-ci` (short, rename-safe, collision-resistant)

### Why This Name?

1. **Short** - 1-2 syllables ("AYCH-ess-lib", "AYCH-ess-see-eye")
2. **Collision-resistant** - Unlikely to be claimed on public PyPI
3. **Rename-safe** - "HS" can be rebranded (HyperSec → HyperStack, etc.)
4. **Available on PyPI** - Both names verified available

### Package Rename Execution Plan

---

## Phase 1: Rename Python Package (hyperlib → hs_lib) - **2h**

**Package directory:**
- Rename: `src/hyperlib/` → `src/hs_lib/`
- Python converts hyphen to underscore in imports: `hs-lib` → `hs_lib`

**Files to update:**
1. `pyproject.toml` - Change `name = "hyperlib"` → `name = "hs-lib"`
2. `pyproject.toml` - Change `include = ["hyperlib*"]` → `include = ["hs_lib*"]`
3. `src/hs_lib/__init__.py` - Update `__version__` docstrings
4. `VERSION` file - No change (version number stays same)

**Git operation:**
```bash
git mv src/hyperlib src/hs_lib
```

---

## Phase 2: Update All Imports and References - **2h**

**Search and replace pattern:**
- `from hs_lib` → `from hs_lib`
- `import hs_lib` → `import hs_lib`
- `hyperlib.` → `hs_lib.`

**Files affected:**
- All Python files in `src/hs_lib/` (internal imports)
- All test files in `tests/`
- All example files in `examples/`
- All documentation code examples in `docs/`

**Verification:**
```bash
# Find any remaining hyperlib references
grep -r "from hs_lib" .
grep -r "import hs_lib" .
grep -r "hyperlib\." . --include="*.py"
```

---

## Phase 3: Update Documentation and Examples - **1h**

**Files to update:**
1. `README.md` - All installation/usage examples
2. `docs/*.md` - All code examples and package name references
3. `examples/*/README.md` - Installation instructions
4. `examples/*/pyproject.toml` - Dependency: `hyperlib` → `hs-lib`
5. `CLAUDE.md` - Package name references

**Search patterns:**
- `hyperlib` → `hs-lib` (package name in text)
- `from hs_lib` → `from hs_lib` (code examples)
- `pip install hs-lib` → `pip install hs-lib`
- `uv add hs-lib` → `uv add hs-lib`

---

## Phase 4: Update CI/CD Configuration - **1h**

**Files to update:**
1. `.github/workflows/*.yml` - Package name references
2. `ci-local/ci.yaml` - Project name
3. `ci/modules/python/templates/pyproject.toml` - Template updates (if any)
4. `ci/modules/python/run.d/51-publish.py` - JFrog publish script (verify package name)
5. `ci/modules/python/run.d/52-verify-publish.py` - Verify script

**JFrog Repository:**
- Package will be published as `hs-lib` to JFrog
- Old `hyperlib` versions remain accessible (no breaking change for existing users)

---

## Phase 5: Test Everything - **1h**

**Test checklist:**
```bash
# 1. Clean rebuild
rm -rf .venv ci-local/.venv dist build src/*.egg-info
./ci/bootstrap install

# 2. Run tests
./ci/run check

# 3. Build package
./ci/run build

# 4. Verify package contents
tar -tzf dist/hs_lib-*.tar.gz | head -20

# 5. Test import in fresh venv
python -m venv /tmp/test-hs-lib
source /tmp/test-hs-lib/bin/activate
pip install dist/hs_lib-*.whl
python -c "from hs_lib import Application; print('OK')"
```

**Expected results:**
- ✅ All tests passing
- ✅ Package builds successfully
- ✅ Package name is `hs-lib` in metadata
- ✅ Import works as `from hs_lib import ...`

---

## Phase 6: Rename GitHub Repositories - **1h**

**Repositories to rename:**

### 6.1 hyperlib → hs-lib
1. Go to: https://github.com/hypersec-io/hyperlib/settings
2. Repository name: `hyperlib` → `hs-lib`
3. GitHub auto-creates redirect: `hyperlib` → `hs-lib`
4. Update description: "HS-Lib: Enterprise Python infrastructure..."

### 6.2 hyperci → hs-ci
1. Go to: https://github.com/hypersec-io/hyperci/settings
2. Repository name: `hyperci` → `hs-ci`
3. GitHub auto-creates redirect: `hyperci` → `hs-ci`
4. Update description: "HS-CI: Unified CI/CD framework..."

**Important:**
- GitHub maintains redirects automatically
- Old URLs still work: `github.com/hypersec-io/hyperlib` → `github.com/hypersec-io/hs-lib`
- Update git remote URLs in local clones:
  ```bash
  git remote set-url origin git@github.com:hypersec-io/hs-lib.git
  git remote set-url origin git@github.com:hypersec-io/hs-ci.git
  ```

---

## Phase 7: Update Downstream Projects (dfe-*) - **2h**

**Projects using hyperlib:**
1. `dfe-ui-backend`
2. `dfe-hunt-runner`
3. `dfe-cli-core`

**For each project:**

1. **Update pyproject.toml dependencies:**
   ```toml
   # OLD
   dependencies = ["hyperlib>=2.8.8"]

   # NEW
   dependencies = ["hs-lib>=2.8.8"]
   ```

2. **Update all Python imports:**
   ```bash
   # Search and replace
   find . -name "*.py" -exec sed -i 's/from hs_lib/from hs_lib/g' {} \;
   find . -name "*.py" -exec sed -i 's/import hs_lib/import hs_lib/g' {} \;
   ```

3. **Update documentation:**
   - README.md installation instructions
   - Any code examples

4. **Update ci/ submodule (if using hyperci):**
   ```bash
   cd ci
   git remote set-url origin git@github.com:hypersec-io/hs-ci.git
   git pull origin main
   cd ..
   git add ci
   git commit -m "fix: update ci submodule (renamed hyperci → hs-ci)"
   ```

5. **Test and commit:**
   ```bash
   ./ci/bootstrap install
   ./ci/run check
   git commit -am "fix: rename hyperlib → hs-lib imports"
   ```

---

## Phase 8: Setup Package Redirects/Aliases - **1h**

**Option A: Keep old name as stub (recommended for grace period)**

Create minimal `hyperlib` package that depends on `hs-lib`:

**File:** `legacy/hyperlib/pyproject.toml`
```toml
[project]
name = "hyperlib"
version = "3.0.0"
dependencies = ["hs-lib>=2.8.8"]
description = "DEPRECATED: Use hs-lib instead"
```

**File:** `legacy/hyperlib/src/hyperlib/__init__.py`
```python
"""
DEPRECATED: hyperlib has been renamed to hs-lib.
This package is a compatibility stub that re-exports hs-lib.

Please update your code:
    from hs_lib import X  →  from hs_lib import X
    pip install hs-lib  →  pip install hs-lib
"""
import warnings
from hs_lib import *  # noqa: F401, F403

warnings.warn(
    "hyperlib has been renamed to hs-lib. "
    "Please update your dependencies and imports. "
    "This compatibility stub will be removed in version 4.0.0.",
    DeprecationWarning,
    stacklevel=2
)
```

**Publish to JFrog:**
```bash
cd legacy/hyperlib
uv build
./ci/run publish
```

**Grace period:** 6-12 months, then remove stub

**Option B: No redirect (hard cutover)**

- Don't publish `hyperlib` v3.0.0
- All users must update to `hs-lib`
- Simpler, but higher friction

**Recommendation:** Use Option A for smoother transition

---

## Phase 9: Update JFrog Repository (Post-Migration) - **0.5h**

**JFrog packages after migration:**
- `hs-lib` - New package (v2.8.8+)
- `hyperlib` - Old versions (v2.8.7 and earlier) remain accessible
- `hyperlib` - Optional compatibility stub (v3.0.0) if using Option A

**No action required:**
- Old versions of `hyperlib` remain in JFrog
- Existing projects can continue using old versions
- New projects use `hs-lib`

---

## Success Criteria

**Code:**
- ✅ Package builds as `hs-lib`
- ✅ All imports use `hs_lib`
- ✅ All tests passing
- ✅ No references to `hyperlib` in code (except deprecation stub)

**Documentation:**
- ✅ README shows `hs-lib` installation
- ✅ All examples use `from hs_lib import ...`
- ✅ GitHub repos renamed with redirects active

**Downstream:**
- ✅ All DFE projects updated
- ✅ All DFE projects tested and passing
- ✅ CI/CD pipelines working

**JFrog:**
- ✅ `hs-lib` published successfully
- ✅ Package discoverable via `pip index versions hs-lib`
- ✅ Old `hyperlib` versions still accessible

---

## Estimated Total Effort

| Phase | Description | Estimate |
|-------|-------------|---------|
| 1 | Rename Python package | **2h** |
| 2 | Update imports/references | **2h** |
| 3 | Update documentation | **1h** |
| 4 | Update CI/CD config | **1h** |
| 5 | Test everything | **1h** |
| 6 | Rename GitHub repos | **1h** |
| 7 | Update downstream (3 projects) | **2h** |
| 8 | Setup redirects/aliases | **1h** |
| 9 | Update JFrog | **0.5h** |

**Total:** **11-12h** (1.5 days)

---

## Migration Commands Cheat Sheet

```bash
# Phase 1: Rename package directory
git mv src/hyperlib src/hs_lib

# Phase 2: Update imports (use with caution, review changes)
find src -name "*.py" -exec sed -i 's/from hs_lib/from hs_lib/g' {} \;
find tests -name "*.py" -exec sed -i 's/from hs_lib/from hs_lib/g' {} \;

# Phase 5: Test
rm -rf .venv ci-local/.venv dist build src/*.egg-info
./ci/bootstrap install
./ci/run check
./ci/run build

# Phase 6: Update git remote
git remote set-url origin git@github.com:hypersec-io/hs-lib.git

# Phase 7: For each downstream project
cd /path/to/dfe-ui-backend
find . -name "*.py" -exec sed -i 's/from hs_lib/from hs_lib/g' {} \;
# Update pyproject.toml manually
./ci/bootstrap install
./ci/run check
```

---

## Rollback Plan

**If migration fails mid-way:**

```bash
# Revert all changes
git reset --hard HEAD
git clean -fd

# Restore package name
git mv src/hs_lib src/hyperlib

# Rebuild
./ci/bootstrap install
./ci/run check
```

**If migration complete but issues found:**

1. Publish hotfix to `hs-lib` with fixes
2. Keep `hyperlib` stub pointing to working version
3. Update downstream projects to working version

---

## Communication Plan

**Internal announcement (before migration):**
```
Subject: Package Rename - hyperlib → hs-lib

We're renaming hyperlib to hs-lib to:
- Avoid collision with public PyPI package "hyperlib"
- Prepare for potential future public release
- Make the name company-rebrand safe

Timeline:
- 2025-11-14: Start migration
- 2025-11-15: Complete hs-lib migration, update all projects
- 2025-11-16: Publish hs-lib v2.8.8 to JFrog
- Grace period: hyperlib stub available for 6 months

Action required:
- Update imports: from hs_lib → from hs_lib
- Update dependencies: hyperlib → hs-lib
- Update git remotes (repos renamed on GitHub)

Questions: #hyperlib on Slack
```

---

## Post-Migration Cleanup (6-12 months)

**After grace period:**

1. Remove `hyperlib` compatibility stub from JFrog
2. Archive old `hyperlib` versions (keep for historical reference)
3. Update all docs to remove mentions of old name
4. Celebrate successful migration 🎉

---

## Active

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
from hs_lib import Application

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
from hs_lib import Application

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
from hs_lib import Application

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

**Last Updated:** 2025-11-13
