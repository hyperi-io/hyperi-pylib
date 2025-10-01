# Hyperlib

HyperSec shared library for Python projects - Enterprise infrastructure for configuration, logging, timeouts, and container management.

## Features

- **Logging**: Structured logging with Loguru and RFC 3339 timestamps
- **Configuration**: Cascading configuration with Dynaconf
- **Bootstrap**: Utilities for project bootstrap (dotenv, script discovery, dependency checking)
- **Caching**: Intelligent caching utilities
- **Resources**: Resource management and cleanup
- **Container**: Dependency injection and service container
- **Timeout**: Async timeout utilities
- **Sampling**: Data sampling utilities

## Installation

### From JFrog Artifactory (Production)

```bash
# Install from HyperSec private PyPI
pip install hyperlib --extra-index-url https://hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local/simple

# With credentials from environment
export JF_USER="your-email@hypersec.io"
export JF_PASSWORD="your-jfrog-password"
pip install hyperlib --extra-index-url "https://${JF_USER}:${JF_PASSWORD}@hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local/simple"
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/hypersec-io/hyperlib
cd hyperlib

# Bootstrap (3-phase: creates .venv-ci, installs hyperlib, runs bootstrap.d scripts)
./scripts/bootstrap --install

# Or set up manually
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick Start

```python
# Logging
from hyperlib import get_logger
logger = get_logger()
logger.info("Application started")

# Configuration
from hyperlib.config import get_logging_config
config = get_logging_config()

# Bootstrap utilities
from hyperlib.bootstrap import load_dotenv, list_sorted_scripts
load_dotenv()
scripts = list_sorted_scripts(Path("scripts/bootstrap.d"))
```

## Local CI (default)

```bash
./scripts/ci
```

CI is local-first. GitHub Actions are disabled by default and should be enabled only for tasks requiring hosted secrets (e.g., publishing).

## Documentation

- **STATE.md** (or CLAUDE.md) - Project state and AI assistant instructions
- **docs/CHARS-POLICY.md** - Character restrictions (ASCII logs, limited emoji)
- **docs/CONTRIBUTING.md** - Development workflow and conventions
- **docs/DEVELOPMENT.md** - Setup, bootstrap, and build instructions
- **docs/ARTIFACTORY.md** - JFrog Artifactory setup and publishing
- **docs/BOOTSTRAP-ANALYSIS.md** - Bootstrap implementation details
- **docs/TEMPLATE-CHANGES.md** - Template change tracking
- **TODO.md** - Authoritative task list
- **CHANGELOG.md** - Version history (auto-generated)

## Requirements

- Python 3.11+
- Dependencies: `loguru`, `dynaconf`, `pyyaml`

## Building and Publishing

```bash
# Build wheel and source distribution
python -m build

# Publish to JFrog Artifactory
python -m twine upload --repository-url https://hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local -u "$JF_USER" -p "$JF_PASSWORD" dist/*
```

## Development

This package is built using the HyperSec Forge template system and serves as a real-world test case for forge-python package template development.

### Testing

```bash
pytest tests/
```

## License

Licensed under HyperSec EULA. See [LICENSE](LICENSE) for details.# Test for release --push
