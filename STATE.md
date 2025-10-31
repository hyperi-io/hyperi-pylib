# Hyperlib - Project State

**Repository**: https://github.com/hypersec-io/hyperlib
**Type**: Python package (shared library)
**Purpose**: Enterprise infrastructure for all HyperSec Python projects
**Version**: 2.4.4
**Latest Published**: 2.4.4 (JFrog, 2025-10-31)

## Session 2025-10-31 Completed

### ONE .venv Migration ✅
- Unified .venv at project root (runtime + CI tools)
- Published v2.4.4 to JFrog (standard + Nuitka x64 + ARM64)

### Nuitka Builds ✅
- Package mode: .whl with .so files (NO .py source)
- App mode: Binary + tarball distribution
- Multi-arch: x64 + ARM64

### uv-Managed Python ✅
- No system Python dependency
- uv downloads Python automatically
- Works on any OS

### Test Status
- HyperCI unit: 56/56 (100%)
- HyperCI integration: 64/64 (100%), 4 skipped
- Hyperlib unit: 121/121 (100%)

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
BUILD_PROFILE=nuitka ./ci/run build
```

## Next: Clean Up ci_lib.py
- Inconsistent naming (some have get_ prefix, some don't)
- Remaining .venv/bin/uv references
- Documentation updates
