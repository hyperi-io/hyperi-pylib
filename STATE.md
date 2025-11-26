# hs-lib - Project State

**Repository**: <https://github.com/hypersec-io/hs-lib>
**Type**: Python package (shared library)
**Purpose**: Enterprise infrastructure for all HyperSec Python projects

---

## Session Management

**New session?** Run `/start` to initialise (reads STATE.md, TODO.md, standards)
**Save progress:** Run `/save` to checkpoint

---

## Current Status (2025-11-26)

**Versions:**

- hs-lib: v2.10.5
- hs-ci: v1.19.1 (GitHub Actions architecture)

**Build type:** Native wheel only (no Nuitka)

---

## CI Architecture (hs-ci v1.19.x)

**IMPORTANT:** hs-ci was completely rewritten. No more `./ci/run` scripts.

### Key Changes from Old CI

| Old (v1.11.x) | New (v1.19.x) |
|---------------|---------------|
| `./ci/run check` | GitHub Actions workflows |
| `./ci/run build` | GitHub Actions workflows |
| `./ci/bootstrap install` | GitHub Actions setup actions |
| `ci.yaml` | `.hypersec-ci.yaml` |
| Python scripts in `modules/` | Composable GitHub Actions in `actions/` |

### Configuration

**Single source:** `.hypersec-ci.yaml` (not `ci.yaml`, not `pyproject.toml`)

**Precedence:** env vars (`HYPERCI_*`) > `.hypersec-ci.yaml` > `ci/defaults.yaml`

**Current hs-lib config:**

```yaml
language: python
quality:
  enabled: true
test:
  enabled: true
  coverage: true
build:
  enabled: true
  strategies:
    - native    # Standard wheel only, no Nuitka
publish:
  enabled: true
python:
  source_dir: src
```

### Local Development

No `./ci/run` anymore. Use standard tools directly:

```bash
# Quality checks
ruff check src/ tests/
ruff format src/ tests/

# Tests
pytest tests/

# Build
uv build
```

### CI Pipeline Flow

```text
push → CI workflow (quality → test → build)
tag  → Semantic Release → Publish workflow
```

### Attach/Update CI

```bash
# Update ci submodule
git -C ci fetch origin main
git -C ci reset --hard origin/main
git add ci && git commit -m "chore: update ci submodule"

# Regenerate workflows
./ci/attach.sh --force
```

---

## Architecture Notes

### hs-ci Release System

**hs-ci itself:** semantic-release CLI + .releaserc.json (Node.js)
**Projects using hs-ci:** GitHub Actions workflows (ci.yml, publish.yml, semantic-release.yml)

### Test Projects

- `/projects/ci/tests/external/projects/python/` - Python test projects
- ci-test-simple-cli, ci-test-simple-package

---

## Quick Reference

**Python requirement:** 3.12+

**Local commands:**

```bash
ruff check src/ tests/       # Lint
ruff format src/ tests/      # Format
pytest tests/                # Test
uv build                     # Build wheel
```

**Update ci submodule:**

```bash
git -C ci reset --hard origin/main
./ci/attach.sh --force
git add ci .github/ .hypersec-ci.yaml .releaserc.json
git commit -m "chore: update ci submodule to vX.Y.Z"
```

---

**Last Updated:** 2025-11-26
