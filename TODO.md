# TODO

**Last Updated:** 2025-10-20

## Active ⭐

- [ ] **PHASE 1: Create /ci/ai tool** - IN PROGRESS
  - [ ] Extract code from 95-ai-settings.py into modular ai.d/ scripts
  - [ ] Create /ci/ai master script (bash wrapper + Python)
  - [ ] Create ci/common/ai.d/ modules (10-check, 20-merge, 30-append, 40-create, 50-copy)
  - [ ] Create ci/python/ai.d/ modules (Python-specific)
  - [ ] Test /ci/ai independently
  - [ ] Update bootstrap.d/95-ai-settings.py to thin wrapper
  - [ ] Update all CI documentation

- [ ] **PHASE 2: Standardize config cascade** - PLANNED
  - [ ] Add get_config_cascade() to ci_lib.py
  - [ ] Add ai: section to ci.yaml
  - [ ] Update all ai.d/ scripts to use cascade
  - [ ] Test cascade: CLI > ENV > .env > ci.yaml > defaults
  - [ ] Update CODE-ASSISTANT.md with detailed cascade

## Planned

- [ ] PHASE 3: Refactor /ci/bootstrap and /ci/run (Future)
  - [ ] Standardize bootstrap to use same pattern
  - [ ] Standardize run to use same pattern
  - [ ] Unified config cascade across all tools

## Done ✓

- [x] Dual pre-sync strategy (VERSION corruption prevention)
- [x] settings merge (CI_MERGE)
- [x] Standards directory (CHARS-POLICY, CODE-ASSISTANT, GIT-WORKFLOW)
- [x] Code of Conduct (no marketing, factual language)
- [x] Australian communication style
- [x] Configuration cascade guidance (no hardcoding)
- [x] Logging guidance (use hyperlib)
- [x] Rename  → ai/ (brand-neutral)
- [x] MCP memory server (mcp-knowledge-graph)
- [x] Template substitution for paths ({{PROJECT_ROOT}})

## Backlog

- [ ] Extract hardcoded update script from ci/bootstrap to separate file
- [ ] Add more standards (security, testing, deployment)
- [ ] Create migration guides for other projects

---

**Format Guide:**
- Checkbox: `- [ ]` pending | `- [x]` done | `- [-]` cancelled
- Status: IN PROGRESS, BLOCKED: reason, WAITING: event
- Keep Active small (3-7 items for focus)

**Usage:**
- "Update TODO - mark X as done"
- "Move task X from Planned to Active"
- "Add new task: implement Y"
