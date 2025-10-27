# TODO

**Last Updated:** 2025-10-28

## Active ⭐

(No active tasks)

## Planned

**Future:**
- [ ] Finish hyperlib package development (fix failing tests, improve coverage)
- [ ] Consider adding CI-LOCAL.md to bootstrap.d merge list (currently only in ai setup)

## Done ✓

**Phase 4 Complete (2025-10-28):**
- [x] Bootstrap Testing & File Management
  - Backed up files that bootstrap modifies (./backup/ directory)
  - Tested bootstrap template merge system (idempotent, marker-based)
  - Verified file merge strategies (gitignore, gitattributes, .env.sample, git hooks)
  - Documented parent project file modifications in ci/README.md
- [x] Bootstrap Fixes (HyperCI)
  - Fixed gitci/ai action names (setup -> install)
  - Added path setup boilerplate to ai.d/15-merge-files.py
  - All bootstrap tests pass with no errors (GitCI + AI setup complete)
- [x] Documentation Updates
  - Added comprehensive file modification tables to ci/README.md
  - Documented merge strategies and bootstrap modes
  - Created backup/README.md with restore instructions
  - Created bootstrap-test-results.md (detailed analysis)

**Phase 3 Complete (2025-10-27):**
- [x] Modular .d pattern implementation across all 4 tools (bootstrap, run, ai, gitci)
- [x] Unified commit-msg hook with 4 validations (branch, message, format, AI attribution)
- [x] Enhanced STATE.md templates with comprehensive Python tooling documentation
- [x] Cleaned ci/STATE.md (491 lines) and project STATE.md (318 lines) - removed duplication
- [x] Comprehensive test suite: 79/79 passing (BATS 20, unit 38, integration 21)

**Earlier Phases:**
- [x] Phase 1 & 2 - Modular /ci/ai + Multi-defaults Cascade
- [x] Code Standards - CODE-ASSISTANT.md (965 lines), CODE_HEADER.md (REUSE/SPDX)
- [x] Git hooks - Auto-installed during bootstrap
- [x] Template system - Consolidated in modules/{common,python}/templates/
