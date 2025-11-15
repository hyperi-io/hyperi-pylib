# hs-lib TODO

## Active

### Update Downstream Projects (DFE apps) - **1-2h**

**Status:** hs-lib package rename complete, downstream projects pending

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

### HS-CI Improvements

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
