# TODO

**Last Updated:** 2025-10-22

## Active ⭐

(No active tasks - Phase 2 complete!)

## Planned

- [ ] PHASE 3: Standardize /ci/bootstrap and /ci/run (Future)
  - [ ] Apply same .d pattern to bootstrap
  - [ ] Apply same .d pattern to run
  - [ ] Unified config cascade across all tools

## Done ✓

- [x] **PHASE 2: Standardize config cascade** - COMPLETE ✅
  - [x] Updated all ai.d/ scripts to use get_config_value() from ci_lib.py
  - [x] Added ai: section example to ci.yaml.template
  - [x] Added ai: section to ci-local/ci.yaml (hyperlib)
  - [x] Tested config cascade: CLI > ENV > .env > ci.yaml > defaults
  - [x] Updated CODE-ASSISTANT.md with detailed cascade documentation
  - [x] Updated STATE.md with /ci/ai tool usage guide
  - [x] All changes committed to hyperci and hyperlib

- [x] **PHASE 1: Create /ci/ai tool** - COMPLETE ✅
  - [x] Created /ci/ai master script (bash + Python)
  - [x] Created ci/common/ai.d/ modules (5 files)
  - [x] Created ci/python/ai.d/ module
  - [x] Updated 95-ai-settings.py to 70-line thin wrapper (was 505 lines!)
  - [x] Tested /ci/ai independently - ALL TESTS PASS
  - [x] Enhanced ci_lib.py with config cascade + logging from hyperlib

- [x] Dual pre-sync strategy (VERSION corruption prevention)
- [x] Claude Code settings merge (CI_CLAUDE_MERGE)
- [x] Standards directory (4 files, 1,443 lines)
- [x] CODE-ASSISTANT.md (965 lines with Code of Conduct)
- [x] Australian communication style
- [x] Configuration cascade guidance
- [x] Logging guidance (use hyperlib)
- [x] Rename claude/ → ai/
- [x] MCP servers (sequential-thinking, mcp-knowledge-graph)
- [x] Template substitution ({{PROJECT_ROOT}})

## Backlog

- [x] Extract hardcoded update script from ci/bootstrap
  - ✅ Already done: ci/bootstrap.update-ci.sh exists as separate file
  - ✅ Bootstrap uses template substitution ({{PROJECT_ROOT}}, {{REMAINING_ARGS}})
  - ✅ No embedded shell scripts in Python code

- [x] Migration guides for other projects
  - ✅ Already done: ci/docs/MIGRATE-dfe-hunt-runner.md
  - ✅ Already done: ci/docs/MIGRATE-dfe-ui-backend.md
  - ✅ Already done: ci/docs/MIGRATE-dfe-cli-core.md

- [ ] Add more standards (ongoing)
  - ✅ Existing: CODE-ASSISTANT.md (common + python, 965+ lines)
  - ✅ Existing: CODE-HEADER.md (REUSE/SPDX compliance)
  - ✅ Existing: CHARS-POLICY.md (character restrictions)
  - ✅ Existing: GIT-WORKFLOW.md (git best practices)
  - ✅ Existing: PYTHON-CODING.md (Python-specific standards)
  - Future: Add more as needed

---

**Phase 1 Results:**
✅ /ci/ai check - Works
✅ /ci/ai setup --mode merge - Works  
✅ Backward compat (CI_CLAUDE_MERGE) - Works
✅ Modular (897 lines across 8 files)
✅ Thin wrapper (70 lines, was 505)
