# TODO

**Last Updated:** 2025-10-27

## Active ⭐

(No active tasks)

## Planned

**Tomorrow (Priority 1):**
- [ ] Back up files in hyperlib that new ci bootstrap will merge/overwrite, then delete them (except STATE.md)
  - Files to backup: .gitignore, .gitattributes, ci-local/.env.sample, etc.
  - Keep STATE.md (already has marker for appending)
- [ ] Run new bootstrap against hyperlib project root to test template merges
  - Test: `./ci/bootstrap --install`
  - Verify: File merges work correctly, git hooks installed, venvs created

**Future:**
- [ ] Finish hyperlib package development (fix failing tests, improve coverage)

## Done ✓

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
