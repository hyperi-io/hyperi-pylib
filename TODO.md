# TODO - Hyperlib

Last Updated: 2025-09-30

## Pending

- Remove src/hyperlib/bootstrap.py and move hyperlib-specific code to scripts/bootstrap.d/
  - Rationale: bootstrap.py in src/ creates confusion (package code vs CI tooling)
  - Extract hyperlib-specific bootstrap logic to scripts/bootstrap.d/XX-hyperlib-setup.py
  - Keep only universal bootstrap utilities in hyperlib package (load_dotenv, list_sorted_scripts)
  - Separates package library code from project-specific CI/bootstrap tooling

## In Progress

## Completed

**2025-09-30** - Forge alignment and v1.0.1 release:
- Updated README.md with comprehensive documentation
- Created STATE.md with project state and policies
- Created CLAUDE.md symlink for AI assistant compatibility
- Created TODO.md for task tracking
- Removed bundled `scripts/hyperlib/` (use pip-installed only)
- Updated bootstrap.py to 3-phase approach
- Fixed `__init__.py` exports (get_logger, bootstrap module, etc.)
- Published v1.0.1 to JFrog Artifactory
- Verified bootstrap works with pip-installed hyperlib

**Previous** - v1.0.0 initial release:
- Published to JFrog Artifactory private PyPI
- Core modules: config, logger, timeout, container, cache
- Bootstrap utilities: load_dotenv, list_sorted_scripts, etc.

## Notes
- Keep lightweight and human-editable
- Use simple Markdown lists; no special metadata
- Policy: no emojis in tasks or headings