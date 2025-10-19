#!/usr/bin/env python3
"""
Claude Code Settings Merge (Bootstrap Step)

Merges Claude Code settings from HyperCI into project .claude/ directory.

This allows HyperCI to provide standardized Claude Code configuration while
letting projects customize settings.

Merge Sources (in order):
  1. ci/common/claude/          # Universal settings (all projects)
  2. ci/python/claude/          # Language-specific (Python only)
  3. ci-local/common/claude/    # Project overrides (optional)
  4. ci-local/python/claude/    # Project Python overrides (optional)

Merge Target:
  .claude/                      # Project's Claude Code settings

Environment Control:
  CI_CLAUDE_MERGE=merge         # Overwrite existing settings
  CI_CLAUDE_MERGE=no-overwrite  # Keep existing, only add new
  CI_CLAUDE_MERGE=skip          # Skip Claude settings merge (default - opt-in model)

Run modes:
- check: Verify Claude settings can be merged (always succeeds)
- install: Perform the actual merge

Usage:
    ci-local/.venv/bin/python ci-local/common/bootstrap.d/95-claude-settings.py check
    ci-local/.venv/bin/python ci-local/common/bootstrap.d/95-claude-settings.py install
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Get project root (this script is at ci-local/common/bootstrap.d/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CI_DIR = PROJECT_ROOT / "ci"
CI_LOCAL_DIR = PROJECT_ROOT / "ci-local"
CLAUDE_DIR = PROJECT_ROOT / ".claude"


def deep_merge_json(target: Dict[str, Any], source: Dict[str, Any], overwrite: bool = True) -> Dict[str, Any]:
    """
    Deep merge two JSON dictionaries.

    Args:
        target: Target dictionary (will be modified)
        source: Source dictionary (merged into target)
        overwrite: If True, overwrite existing keys. If False, keep existing.

    Returns:
        Merged dictionary
    """
    for key, value in source.items():
        if key in target:
            # Key exists in target
            if isinstance(target[key], dict) and isinstance(value, dict):
                # Both are dicts, recurse
                target[key] = deep_merge_json(target[key], value, overwrite)
            elif overwrite:
                # Overwrite existing value
                target[key] = value
            # else: keep target[key] (no-overwrite mode)
        else:
            # New key, always add
            target[key] = value

    return target


def merge_json_file(target_file: Path, source_file: Path, overwrite: bool = True) -> bool:
    """
    Merge a JSON file from source into target.

    Args:
        target_file: Target JSON file (in .claude/)
        source_file: Source JSON file (from ci/ or ci-local/)
        overwrite: If True, overwrite existing keys

    Returns:
        True if merge was performed, False if skipped
    """
    if not source_file.exists():
        return False

    # Load source
    try:
        with open(source_file) as f:
            source_data = json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load {source_file}: {e}")
        return False

    # Load target (or start with empty dict)
    target_data = {}
    if target_file.exists():
        try:
            with open(target_file) as f:
                target_data = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load {target_file}, starting fresh: {e}")

    # Merge
    merged_data = deep_merge_json(target_data, source_data, overwrite)

    # Write back
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, 'w') as f:
        json.dump(merged_data, f, indent=2)
        f.write('\n')  # Add trailing newline

    return True


def copy_file(target_file: Path, source_file: Path, overwrite: bool = True) -> bool:
    """
    Copy a file from source to target.

    Args:
        target_file: Target file path
        source_file: Source file path
        overwrite: If True, overwrite existing file

    Returns:
        True if copy was performed, False if skipped
    """
    if not source_file.exists():
        return False

    # Skip if target exists and overwrite is False
    if target_file.exists() and not overwrite:
        return False

    # Copy
    target_file.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy2(source_file, target_file)
    return True


def merge_claude_settings(merge_mode: str = "merge") -> int:
    """
    Merge Claude Code settings from ci/ and ci-local/ into .claude/.

    Args:
        merge_mode: "merge" (overwrite), "no-overwrite" (keep existing), or "skip"

    Returns:
        0 on success, 1 on failure
    """
    if merge_mode == "skip":
        print("[INFO] CI_CLAUDE_MERGE=skip, skipping Claude settings merge")
        return 0

    overwrite = (merge_mode == "merge")
    mode_label = "OVERWRITE" if overwrite else "NO-OVERWRITE"

    print(f"[INFO] Merging Claude settings (mode: {mode_label})...")

    # Discover source directories (in order)
    source_dirs = [
        CI_DIR / "common" / "claude",
        CI_DIR / "python" / "claude",
        CI_LOCAL_DIR / "common" / "claude",
        CI_LOCAL_DIR / "python" / "claude",
    ]

    # Track what was merged
    merged_files = []

    # Merge settings.json from all sources
    for source_dir in source_dirs:
        settings_file = source_dir / "settings.json"
        if settings_file.exists():
            if merge_json_file(CLAUDE_DIR / "settings.json", settings_file, overwrite):
                merged_files.append(f"  settings.json ← {source_dir.relative_to(PROJECT_ROOT)}")

    # Copy command files (*.md) from all sources
    for source_dir in source_dirs:
        commands_dir = source_dir / "commands"
        if not commands_dir.exists():
            continue

        for source_file in commands_dir.glob("*.md"):
            target_file = CLAUDE_DIR / "commands" / source_file.name
            if copy_file(target_file, source_file, overwrite):
                merged_files.append(f"  commands/{source_file.name} ← {source_dir.relative_to(PROJECT_ROOT)}")

    if merged_files:
        print(f"[INFO] Merged {len(merged_files)} Claude settings file(s):")
        for f in merged_files:
            print(f)
    else:
        print("[INFO] No Claude settings to merge (no source files found)")

    return 0


def check_claude_settings() -> int:
    """
    Check if Claude settings can be merged (always succeeds).

    This is a no-op check that always passes. The actual merge happens
    during 'install' phase.

    Returns:
        0 (always succeeds)
    """
    print("[INFO] Claude settings merge check (no-op, always passes)")
    return 0


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("ERROR: Usage: 95-claude-settings.py [check|install]")
        return 1

    action = sys.argv[1]

    # Get merge mode from environment (default: skip - opt-in model)
    merge_mode = os.environ.get("CI_CLAUDE_MERGE", "skip").lower()
    valid_modes = ["merge", "no-overwrite", "skip"]

    if merge_mode not in valid_modes:
        print(f"[WARN] Invalid CI_CLAUDE_MERGE='{merge_mode}', using 'merge'")
        merge_mode = "merge"

    if action == "check":
        return check_claude_settings()

    elif action == "install":
        return merge_claude_settings(merge_mode)

    else:
        print(f"ERROR: Unknown action '{action}'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
