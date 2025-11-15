# hs-lib - Project State

**Repository**: https://github.com/hypersec-io/hs-lib
**Type**: Python package (shared library)
**Purpose**: Enterprise infrastructure for all HyperSec Python projects

---

## 🔄 SESSION MANAGEMENT

**IMPORTANT:** If this is a new session or context was compressed:
1. **Run `/start` command** to initialize the session properly
2. Read STATE.md, TODO.md, and standards documentation
3. Confirm ready before proceeding with work

**Save progress anytime:** Run `/save` to checkpoint progress, clean up STATE.md and TODO.md (can run multiple times per session)

---

## Current Status (2025-11-15)

**Active work:**
- Package rename: hyperlib → hs-lib (PARTIALLY COMPLETE)
  - ✅ Source renamed: `src/hs_lib/`
  - ✅ Package name: `hs-lib` in pyproject.toml
  - ✅ Documentation updated
  - ⏳ Full import migration pending (see TODO.md)

**Recent completions:**
- ✅ CI and AI finalization (Python 3.12, dual-pattern permissions, hs-ci rename)
- ✅ Container-native patterns (all 4 phases complete)
- ✅ Strong WIP warning for Application framework

**Versions:**
- hs-lib: v2.9.1
- hs-ci: v1.6.15

---

## Session 2025-11-15 - CI and AI Finalization

### Comprehensive Permission System - Complete ✅

**Dual-pattern Bash permissions:**
- Both `Bash(command *)` AND `Bash(command:*)` for all tools
- Colon `:*` operator means "continuation from preceding string" (reliable)
- Space `*` provides fallback coverage
- SlashCommand permissions for `/start` and `/save`

**Key improvements:**
- Git commands (especially `git -C` for submodule work)
- All development tools (uv, pytest, ruff, black, docker, kubectl, etc.)
- CI commands (./ci/bootstrap, ./ci/run, ./ci/ai)

### Python 3.12 Migration - Complete ✅

**Updated:**
- ✅ hs-lib requires Python 3.12
- ✅ hs-ci templates require Python 3.12
- ✅ All tool configs (ruff, black, pyright, mypy)
- ✅ Fixed duplicate pytest markers in hs-lib

### Repository Rename - Complete ✅

**hs-ci (formerly hyperci):**
- ✅ Repository URL in .releaserc.json
- ✅ All documentation (hyperci → hs-ci)
- ✅ Generic templates (hyperlib → PROJECT_NAME)
- ✅ v1.6.15 released (NO breaking changes!)

**hs-lib (formerly hyperlib):**
- ✅ Documentation renamed
- ✅ Badges updated (removed version badge)
- ✅ Repository URLs corrected

### Settings Cleanup - Complete ✅

- ✅ Removed settings.local.json template (obsolete)
- ✅ ENV vars now in ~/.bashrc (via 20-bashrc-env.py)
- ✅ .pip/pip.conf removed from git tracking (contains credentials)
- ✅ .pip/ properly gitignored

### Critical Lesson Learned

**NEVER add "Breaking change:" to commit messages unless it actually breaks backward compatibility!**
- Avoided v2.0.0 major bump by removing the marker
- Python version updates are NOT breaking changes (gradual adoption)
- Semantic-release strictly follows Conventional Commits spec

---

## Architecture Notes

### hs-ci Release System (Two Separate Systems)

**1. hs-ci ITSELF:**
- Location: `/projects/hs-lib/ci` (git submodule)
- Automation: semantic-release CLI + .releaserc.json (Node.js)
- Avoids circular dependency (infrastructure shouldn't depend on itself)

**2. hs-ci AS A SERVICE (for parent projects):**
- Location: Parent project uses `/ci` as submodule
- Automation: Python-based `./ci/run release`
- Full orchestration with Python semantic-release, VERSION sync, badge updates

---

## Quick Reference

**Current Python requirement:** 3.12+

**hs-ci version:** v1.6.15

**hs-lib version:** v2.9.1

**Test status:** All passing

---
