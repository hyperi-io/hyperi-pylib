# Hyperlib

HyperSec shared library for Python projects.

## Overview

Hyperlib provides common utilities and patterns used across HyperSec Python projects:

- **Logging**: Structured logging with Loguru
- **Configuration**: Cascading configuration with Dynaconf  
- **Caching**: Intelligent caching utilities
- **Resources**: Resource management and cleanup
- **Container**: Dependency injection and service container
- **Timeout**: Async timeout utilities
- **Sampling**: Data sampling utilities

## Installation

### Development

```bash
pip install -e .
```

### Production (Future)

```bash
pip install hyperlib --index-url https://hypersec.jfrog.io/artifactory/api/pypi/hypersec-pypi-local/simple
```

## Development

This package is built using the HyperSec Forge template system.

### Testing

```bash
pytest tests/
```

### Building

```bash
python -m build
```

## License

HyperSec EULA - Proprietary