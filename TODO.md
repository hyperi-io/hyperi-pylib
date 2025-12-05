# hs-lib TODO

## Active

### Debug GitHub Actions bootstrap failures - **2h** 🟡

**Status:** HS_CI_PAT works for checkout, bootstrap failing

**Problem:**
- uv sync/lock/build fail in GitHub Actions environment
- Works locally with same configuration
- May be env var propagation or uv version differences

**Next:**
- Verify UV_INDEX_JFROG credentials actually set in GHA environment
- Check if --index-strategy flags working in GHA
- Consider sourcing .env before bootstrap or different export method

### Skip standard build matrix entry for apps - **0.5h**

**Status:** Apps shouldn't have standard-any build job at all

**Task:**
- Update matrix generation in workflow to skip standard build when build_type: app
- Only include Nuitka builds (x64, arm64) for apps
- Standard build only for packages

### Replace HS_CI_PAT with GitHub App token - **4h**

**Status:** PAT is user-tied, need corporate solution

**Task:**
- Create GitHub App for CI with contents:read permission
- Use actions/create-github-app-token@v1 in workflows
- Update all workflows to use app token
- Remove HS_CI_PAT secret

---

## Backlog

### Add hs_lib.cache module (Cashews wrapper) - **4h**

**Status:** Not started - identified as gap during dfe-control-plane metrics work

**Solution:** Wrap [Cashews](https://github.com/Krukov/cashews) (527 stars, MIT, active)

**Task:**
- Create `hs_lib.cache` module wrapping Cashews with disk backend
- Cache tuple: `(source, identifier, value, time)` - source-based TTLs
- Per-source TTL config: `{"http": "24h", "tavily": "1h", "db": "30m"}`
- `@cached("http", key="{url}")` decorator
- Built-in metrics (hit/miss) via hs_lib.metrics

**Dependencies:**
```toml
"cashews[diskcache]>=7.0"
```

**Rationale:**
- Disk-backed (SQLite) reduces memory, survives restarts
- Native async, FastAPI integration
- Thin wrapper around battle-tested library

**Design:** See dfe-control-plane/HS-LIB-UPDATE.md §5

### Add hs_lib.http.HttpClient (Stamina + httpx) - **3h**

**Status:** Not started - identified during dfe-control-plane B113 fixes

**Solution:** Wrap [Stamina](https://github.com/hynek/stamina) (by Hynek, attrs/structlog author) + httpx

**Task:**

- Create `hs_lib.http.HttpClient` wrapping httpx + stamina
- Auto timeout (default 30s) - solves B113 bandit issues
- Auto retries with exponential backoff via stamina
- Stamina auto-detects structlog + prometheus-client

**Dependencies:**

```toml
"httpx>=0.27"
"stamina>=25.1"
```

**Rationale:**

- Stamina auto-integrates with hs_lib.logger (structlog) and hs_lib.metrics (prometheus)
- Testing friendly: `stamina.set_testing(attempts=1)` in pytest
- Same author as attrs/structlog - quality pedigree

**Design:** See dfe-control-plane/HS-LIB-UPDATE.md §4

### Add FastAPI metrics middleware to hs_lib.metrics - **2h**

**Status:** Not started - identified during dfe-control-plane metrics work

**Task:**
- Create `hs_lib.metrics.fastapi.PrometheusMiddleware`
- Auto-track: request count, duration, status by endpoint
- Create `hs_lib.metrics.fastapi.create_metrics_router()` for `/metrics` endpoint
- Zero-config: `app.add_middleware(PrometheusMiddleware)`

**Rationale:**
- All FastAPI apps need HTTP metrics
- Currently each app implements manually
- Consistency across HyperSec apps

### Add DB query metrics helpers to hs_lib.metrics - **1h**

**Status:** Not started - identified during dfe-control-plane metrics work

**Task:**
- Create context manager: `with metrics.db_query("postgres", "select"): ...`
- Create decorator: `@metrics.track_db_query(db_type="clickhouse")`
- Works with any DB client (not auto-instrumented)

**Rationale:**
- Multiple DB types (ClickHouse, Postgres, FalconDB)
- Can't auto-instrument all clients
- Explicit instrumentation is reliable

### Add hs_lib.kafka module (confluent-kafka wrapper) - **8h**

**Status:** Not started - designed for dfe-discovery Kafka backend support

**Solution:** Wrap [confluent-kafka](https://github.com/confluentinc/confluent-kafka-python) with corporate defaults

**Scope:** Building blocks only - discovery-specific logic stays in dfe-control-plane

**Task:**

1. **KafkaClient** - Admin operations
   - `list_topics()` → `list[TopicInfo]`
   - `describe_topic(topic)` → `TopicMetadata` (partitions, offsets, config)
   - `get_offsets_for_times(topic, timestamps)` → `dict[int, int]`
   - `get_consumer_lag(group, topic)` → `dict[int, int]`

2. **KafkaProducer** - Producer with corporate defaults
   - Corporate defaults: acks=all, idempotence, lz4 compression, retries
   - `send(topic, value, key=None, headers=None)` → `Future`
   - `flush(timeout=None)` → `int`
   - Prometheus metrics integration
   - Sync and async interfaces

3. **KafkaConsumer** - Consumer with corporate defaults
   - Corporate defaults: manual commit, earliest offset, safe timeouts
   - `subscribe(topics)`, `poll(timeout)`, `seek(partition, offset)`
   - `commit()`, `committed(partitions)`
   - Iterator interface: `for msg in consumer: ...`
   - Prometheus metrics integration

4. **Sampling utilities** - Generic sampling (not discovery-specific)
   - `time_bounded_consume(consumer, topic, start, end, limit)` → `list[Message]`
   - `reservoir_sample(consumer, topic, k)` → `list[Message]`
   - `partition_sample(client, topic, n_per_partition)` → `list[Message]`

5. **Schema detection** - Infer and analyse JSON schemas from samples
   - `SchemaAnalyser` class using [GenSON](https://github.com/wolverdude/GenSON) for schema inference
   - `analyse_sample(messages)` → `SchemaAnalysisResult`
   - Detect multiple schema patterns (not all messages have same structure)
   - Calculate field cardinality (distinct values per field)
   - Detect field types with variance (e.g., field is sometimes string, sometimes int)
   - Schema drift detection (compare schemas across time windows)

   ```python
   @dataclass
   class SchemaPattern:
       schema: dict                    # JSON Schema (GenSON output)
       message_count: int              # Messages matching this pattern
       percentage: float               # % of total sample
       example_message: dict           # One example

   @dataclass
   class FieldStats:
       name: str
       types_seen: list[str]           # ["String", "Int64", "null"]
       cardinality: int                # Distinct values
       null_count: int
       sample_values: list[Any]        # Top 5 example values

   @dataclass
   class SchemaAnalysisResult:
       total_messages: int
       patterns: list[SchemaPattern]   # Distinct schema patterns found
       field_stats: dict[str, FieldStats]  # Per-field statistics
       merged_schema: dict             # GenSON merged schema
       schema_consistency: float       # 0-1 (1 = all same schema)
   ```

6. **Async support** - ThreadPoolExecutor wrappers for FastAPI compatibility
   - `AsyncKafkaClient` - async admin operations
   - `AsyncKafkaConsumer` - async iteration, poll
   - `AsyncKafkaProducer` - async send
   - `areservoir_sample()`, `atime_bounded_consume()` - async sampling
   - All async classes wrap sync confluent-kafka via ThreadPoolExecutor
   - Optional: aiokafka consumer for high-throughput streaming (Phase 2)

   ```python
   # Sync (CLI, batch jobs, scripts)
   from hs_lib.kafka import KafkaClient, KafkaConsumer, reservoir_sample

   client = KafkaClient(bootstrap_servers)
   topics = client.list_topics()  # Sync

   # Async (FastAPI, async apps)
   from hs_lib.kafka import AsyncKafkaClient, AsyncKafkaConsumer, areservoir_sample

   async with AsyncKafkaClient(bootstrap_servers) as client:
       topics = await client.list_topics()  # Async
   ```

7. **Types and config**
   - `Message`, `TopicInfo`, `TopicMetadata`, `PartitionInfo`
   - `PRODUCER_DEFAULTS`, `CONSUMER_DEFAULTS`, `ADMIN_DEFAULTS`
   - Config cascade integration (bootstrap.servers from settings)
   - **Config naming**: Use [librdkafka configuration names](https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md) directly
     - e.g., `bootstrap.servers`, `security.protocol`, `sasl.mechanism`
     - No aliasing or renaming - maintain compatibility with Kafka ecosystem
   - **TLS options**: Support `enable.ssl.certificate.verification=false` for testing with self-signed certs
     - Convenience helper: `KafkaClient(..., verify_ssl=False)` sets the librdkafka config

**Corporate Defaults:**

```python
PRODUCER_DEFAULTS = {
    "acks": "all",
    "enable.idempotence": True,
    "retries": 5,
    "retry.backoff.ms": 100,
    "delivery.timeout.ms": 120000,
    "linger.ms": 5,
    "compression.type": "lz4",
}

CONSUMER_DEFAULTS = {
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
    "session.timeout.ms": 45000,
    "heartbeat.interval.ms": 3000,
    "max.poll.interval.ms": 300000,
}
```

**Dependencies:**

```toml
[project.optional-dependencies]
kafka = [
    "confluent-kafka>=2.3",
    "genson>=1.3",  # JSON schema inference
]
```

**Rationale:**
- confluent-kafka is fastest (librdkafka C), full admin API, Confluent backing
- Building blocks enable dfe-control-plane to build KafkaDiscoveryService
- No discovery-specific logic here - that stays in dfe-control-plane
- Matches hs_lib.http pattern (corporate defaults + observability)

**Consumer:** dfe-control-plane KafkaDiscoveryService (see TODO-KAFKA-DISCOVERY.md)

**Design:** Discussed in hs-lib session 2025-12-05

---

## Backlog (CI/Build)

### Allow null/none in ci.yaml to skip tests/linters - **1h**

**Status:** Add flexibility to completely disable checks

**Task:**
- Support `tests: null` or `tests.required: false` to skip all tests
- Support `linters: null` or `linters.required: false` to skip all linters
- Check/fix overlapping code in CI scripts for this logic
- Document in ci.yaml schema

### Fix vermin scan error - **0.5h**

**Status:** Non-blocking warning during linting

**Error:** `2025-11-19T00:38:09.191+1100 | ERROR | __main__:run_vermin_scan:75 - Failed to run vermin: %s`

**Task:**
- Check why vermin scan fails
- Fix or remove vermin if not needed
- Currently just shows warning, doesn't block

### Fix 61-update-badges.py local failure - **1h**

**Status:** Fails during local `./ci/run release`

**Task:**
- Investigate why badge update fails locally
- May need GitHub API credentials or just skip for local releases
- Low priority (doesn't affect GitHub Actions)

### Complete two-venv reference cleanup - **1h**

**Status:** Partially done, docs still need cleanup

**Task:**
- Fix remaining 12+ files in docs/ with ci-local/.venv references
- Update documentation to reflect unified .venv
- Files: docs/standards/, CONTRIBUTING.md, templates/

### Standardize ci_lib path injection - **2h**

**Status:** User wants simpler pattern (not full walk)

**Task:**
- 37 scripts currently use walk-up pattern for ci_lib
- Create simpler, consistent pattern
- Apply to all scripts uniformly

### Create test-package-build project - **2h**

**Status:** Need package mode testing (not just app mode)

**Task:**
- Create under hypersec-io org (private repo)
- Configure build_type: package (not app)
- Test Nuitka package mode (.so compilation)
- Verify compiled wheels work

### Document CI directory structure and naming conventions - **0.5h**

**Status:** Clarify architecture and naming patterns

**Task:**
- Document why we have ci/modules/python/tools vs hs-lib package
- Explain .d directory pattern (bootstrap.d, run.d)
- Clarify naming: hs-lib (package), hs-ci (CI system)
- Add architecture notes to STATE.md or separate doc

### Clean up deprecated CI directories - **0.5h**

**Status:** Audit and remove unused directories

**Task:**
- Check if ci/modules/python/gitci/ is still used (remove if not)
- Check if ci/modules/python/ai/claude/ is still used (templates now?)
- Audit ci/modules/ for any other deprecated directories
- Remove unused code and consolidate

### Handle No Initial Commit Scenario - **2h**

**Status:** Edge case handling

**Task:**
- Handle repositories with no commits yet
- Graceful fallbacks in git log commands
- Clear error messages when git history needed but missing

---

## Completed (2025-11-19)

### pyproject.toml Merge Bug - **3h** ✅

**Fixed:** 35-set-license.py destroying TOML structure with text manipulation
**Solution:** Use tomllib + tomli_w for proper parsing
**Result:** Template dependencies merge correctly

### Dual PyPI Setup for uv - **4h** ✅

**Implemented:** [[tool.uv.index]] + unsafe-best-match strategy
**Result:** Can use private (JFrog) + public (PyPI) packages together

### App vs Package Build Logic - **2h** ✅

**Fixed:** Apps no longer build wheels, only Nuitka binaries
**Updated:** 50-build.py, 55-build-nuitka.py, semantic-release build_command

### Local Nuitka Build Testing - **1h** ✅

**Verified:** test-cli-build builds 14MB Nuitka binary locally
**Works:** Binary executes and is properly encrypted

---

**Last Updated:** 2025-12-05
