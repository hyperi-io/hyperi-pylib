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

**Save progress anytime:** Run `/save` to checkpoint progress, clean up STATE.md and TODO.md

---

## Current Status (2025-11-15)

**Versions:**
- hs-lib: v2.9.1
- hs-ci: v1.6.17 (latest)

**Active work:**
- Package rename partially complete (see TODO.md)
- CI and AI finalization: COMPLETE ✅

**Test status:** All passing

---

## Session 2025-11-15 - CI and AI Finalization

### Claude Code 2.0 Permission System - Complete ✅

**Dual-pattern Bash permissions:**
- Researched Claude Code 2.0 syntax (colon `:*` operator)
- Colon operator means "continuation from preceding string"
- Implemented both `Bash(command *)` AND `Bash(command:*)` patterns
- Comprehensive coverage: git, uv, pytest, docker, kubectl, all dev tools
- SlashCommand permissions for `/start` and `/save`

**Key fix:** `git -C` permission (major pain point for submodule work)

**Files updated:**
- [ci/modules/common/templates/settings.json](ci/modules/common/templates/settings.json) - Template with all permissions
- [.claude/settings.json](.claude/settings.json) - Local with dual patterns (gitignored)

### Python 3.12 Migration - Complete ✅

**Updated across both repositories:**
- ✅ hs-lib requires Python 3.12
- ✅ hs-ci templates require Python 3.12
- ✅ All tool configs (ruff, black, pyright, mypy)
- ✅ Fixed duplicate pytest markers in hs-lib

**Critical lesson:** Removed "Breaking change:" from commit to avoid v2.0.0 major bump
- Deleted v2.0.0 release
- Rewrote git history to remove breaking change marker
- Re-released as v1.6.12 (patch, correct)
- Python version updates are NOT breaking (gradual adoption)

### Repository Rename - Complete ✅

**hs-ci (formerly hyperci):**
- ✅ Repository URL in .releaserc.json
- ✅ All documentation updated
- ✅ Generic templates (hyperlib → PROJECT_NAME)
- ✅ Workflow now passing (was failing due to URL mismatch)

**hs-lib (formerly hyperlib):**
- ✅ README badges updated (removed version badge, Python 3.12+)
- ✅ All documentation renamed
- ✅ Examples updated
- ✅ Strong WIP warning for Application framework

### Settings Cleanup - Complete ✅

- ✅ Removed settings.local.json from deployment (obsolete)
- ✅ ENV vars now in ~/.bashrc (via 20-bashrc-env.py)
- ✅ Removed .pip/pip.conf from git tracking (credentials)
- ✅ Verified .pip/ properly gitignored

### Documentation Rationalization - Complete ✅

**Massive cleanup:**
- hs-lib STATE.md: 3191 → 118 lines (96% reduction!)
- hs-lib TODO.md: 1164 → 83 lines (93% reduction!)
- hs-ci STATE.md: 559 → 119 lines (78% reduction!)
- **Total: Removed 4273 lines of stale content**

**Standards consolidation:**
- Merged Derek's communication preferences into AI-GUIDELINES.md
- Consolidated Australian/American English spelling guide
- Removed duplicate Communication Style from COMMON.md
- Clear separation: COMMON = workflow, AI-GUIDELINES = code quality

### File Structure Clarity

**code-assistant/ standards:**
- **COMMON.md** - Workflow, process, session management, tools
- **AI-GUIDELINES.md** - Code quality, communication style, spelling guide
- **HYPERCI.md** - HS-CI specific workflow
- **PYTHON.md** - Python specific guidance

**ci-local/code-assistant/:**
- **DEREK-PREFERENCES.md** - Derek's personal preferences (loaded by `/start`)

---

## Architecture Notes

### hs-ci Release System (Two Separate Systems)

**1. hs-ci ITSELF:**
- Automation: semantic-release CLI + .releaserc.json (Node.js)
- Avoids circular dependency

**2. hs-ci AS A SERVICE:**
- Automation: Python-based `./ci/run release`
- Full orchestration for parent projects

---

## Quick Reference

**Python requirement:** 3.12+

**Test command:** `./ci/run check`

**Update ci:** `cd ci && git pull origin main && cd .. && git add ci && git commit -m "chore: update hs-ci submodule"`

---

**Last Updated:** 2025-11-15
