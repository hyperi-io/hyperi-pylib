# hs-lib TODO

## Active

### Complete Package Rename (hyperlib → hs-lib) - **Remaining: 4-6h**

**Status:** Source and docs renamed, full migration pending

**Completed:**
- ✅ Source directory: `src/hs_lib/`
- ✅ Package name: `hs-lib` in pyproject.toml
- ✅ Documentation: All user-facing docs updated
- ✅ Examples: Updated to hs-lib
- ✅ Repository name: Reflects hs-lib branding

**Remaining phases:**

#### Phase 1: Verify Source Code Imports - **1h**
- Search for any remaining `from hyperlib` or `import hyperlib` in src/
- Update any internal references (unlikely - already renamed)
- Run tests to verify everything works

#### Phase 2: Update Test Files - **1h**
- Update any hyperlib references in test files
- Update test docstrings and comments
- Verify all tests pass

#### Phase 3: Clean Build Artifacts - **0.5h**
- Remove .tmp/ old hyperlib artifacts
- Clear .mypy_cache
- Clear __pycache__ files
- Fresh build and test

#### Phase 4: GitHub Repository Rename - **1h**
- Rename: hypersec-io/hyperlib → hypersec-io/hs-lib
- GitHub auto-creates redirect
- Update git remote in local clones
- Update CI/CD workflows if needed

#### Phase 5: Update Downstream Projects (DFE apps) - **1-2h**
- dfe-ui-backend: Update dependency and imports
- dfe-hunt-runner: Update dependency and imports
- dfe-cli-core: Update dependency and imports
- Test all three projects

---

## Backlog

### Container-Native Patterns - Phase 4 Improvements

**Status:** Phases 1-3 complete, Phase 4 docs exist but need refinement

- Improve KUBERNETES.md examples
- Add more HELM chart variations
- Expand example projects with real-world scenarios

**Note:** Application framework marked as WIP with strong warning (will be refactored/replaced)

---

### HyperCI Improvements

**Based on principles review**

#### Short-term
- Add `./ci/ai refresh` command - **2h**
- Improve error message consistency - **4h**
- Document two-venv pattern clearly - **1h**

#### Medium-term
- Complete single .venv migration - **8h**
- Add `./ci/run fix` command - **2h**
- Enhance pre-commit hooks - **4h**

#### Long-term
- Unified error reporter - **8h**
- AI-assisted auto-fix - **16h**
- Smart context switching detection - **4h**

---

**Last Updated:** 2025-11-15
