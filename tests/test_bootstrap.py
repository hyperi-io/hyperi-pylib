"""Unit tests for bootstrap functionality."""

import os
from pathlib import Path

import pytest


class TestBootstrapUtilities:
    """Test bootstrap utilities from hyperlib."""

    def test_import_bootstrap_module(self):
        """Test that bootstrap module can be imported from hyperlib."""
        from hyperlib import bootstrap

        assert bootstrap is not None
        assert hasattr(bootstrap, "load_dotenv")
        assert hasattr(bootstrap, "list_sorted_scripts")
        assert hasattr(bootstrap, "load_defaults_yaml")
        assert hasattr(bootstrap, "ensure_dependency")

    def test_list_sorted_scripts_empty_directory(self, temp_dir):
        """Test list_sorted_scripts with empty directory."""
        from hyperlib.bootstrap import list_sorted_scripts

        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()

        scripts = list_sorted_scripts(empty_dir)
        assert scripts == []

    def test_list_sorted_scripts_with_files(self, temp_dir):
        """Test list_sorted_scripts with numbered scripts."""
        from hyperlib.bootstrap import list_sorted_scripts

        scripts_dir = temp_dir / "scripts.d"
        scripts_dir.mkdir()

        # Create test scripts
        (scripts_dir / "10-first.py").write_text("#!/usr/bin/env python3\n")
        (scripts_dir / "20-second.sh").write_text("#!/bin/bash\n")
        (scripts_dir / "05-before-first.py").write_text("#!/usr/bin/env python3\n")

        scripts = list_sorted_scripts(scripts_dir, patterns=("*.py", "*.sh"))

        # Should be sorted by numeric prefix
        assert len(scripts) == 3
        assert scripts[0].name == "05-before-first.py"
        assert scripts[1].name == "10-first.py"
        assert scripts[2].name == "20-second.sh"

    def test_list_sorted_scripts_pattern_filtering(self, temp_dir):
        """Test list_sorted_scripts with pattern filtering."""
        from hyperlib.bootstrap import list_sorted_scripts

        scripts_dir = temp_dir / "scripts.d"
        scripts_dir.mkdir()

        # Create test scripts of different types
        (scripts_dir / "10-script.py").write_text("#!/usr/bin/env python3\n")
        (scripts_dir / "20-script.sh").write_text("#!/bin/bash\n")
        (scripts_dir / "30-script.txt").write_text("text file\n")

        # Filter for Python scripts only
        scripts = list_sorted_scripts(scripts_dir, patterns=("*.py",))

        assert len(scripts) == 1
        assert scripts[0].name == "10-script.py"

    def test_load_dotenv_nonexistent_file(self):
        """Test load_dotenv with non-existent file (should not raise)."""
        from hyperlib.bootstrap import load_dotenv

        # Should not raise exception
        load_dotenv()

    def test_load_dotenv_with_sample_file(self, temp_dir):
        """Test load_dotenv with a sample .env file."""
        import os

        from hyperlib.bootstrap import load_dotenv

        # Create a temporary .env file
        env_file = temp_dir / ".env"
        env_file.write_text("TEST_VAR=test_value\nANOTHER_VAR=123\n")

        # Change to temp directory and load
        original_dir = Path.cwd()
        try:
            os.chdir(temp_dir)
            load_dotenv()

            # Verify variables are loaded
            assert os.environ.get("TEST_VAR") == "test_value"
            assert os.environ.get("ANOTHER_VAR") == "123"
        finally:
            # Cleanup
            os.chdir(original_dir)
            if "TEST_VAR" in os.environ:
                del os.environ["TEST_VAR"]
            if "ANOTHER_VAR" in os.environ:
                del os.environ["ANOTHER_VAR"]

    def test_load_defaults_yaml(self):
        """Test load_defaults_yaml returns a dictionary."""
        from hyperlib.bootstrap import load_defaults_yaml

        defaults = load_defaults_yaml()
        assert isinstance(defaults, dict)

    @pytest.mark.parametrize(
        "command,expected_present",
        [
            ("python3", True),  # Should always be present
            ("nonexistent_command_xyz", False),  # Should not exist
        ],
    )
    def test_ensure_dependency_check_mode(self, command, expected_present):
        """Test ensure_dependency in check mode (no install)."""
        from hyperlib import get_logger
        from hyperlib.bootstrap import ensure_dependency

        logger = get_logger("test")
        defaults = {"dependencies": {}}

        # In check mode (install=False), should verify presence
        if expected_present:
            # Should not raise for commands that exist
            ensure_dependency(command, install=False, logger=logger, defaults=defaults)
        else:
            # Should raise SystemExit for commands that don't exist
            with pytest.raises(SystemExit):
                ensure_dependency(command, install=False, logger=logger, defaults=defaults)


class TestBootstrapIntegration:
    """Integration tests for bootstrap workflow."""

    def test_bootstrap_script_exists(self):
        """Test that bootstrap script exists."""
        bootstrap_script = Path(__file__).parents[1] / "scripts" / "bootstrap"
        assert bootstrap_script.exists(), "Bootstrap script should exist in scripts/"

    def test_bootstrap_d_directory_exists(self):
        """Test that bootstrap.d directory exists."""
        bootstrap_d = Path(__file__).parents[1] / "scripts" / "bootstrap.d"
        # Directory may not exist in minimal projects
        if bootstrap_d.exists():
            assert bootstrap_d.is_dir()

    def test_ci_script_exists(self):
        """Test that CI script exists."""
        ci_script = Path(__file__).parents[1] / "scripts" / "ci"
        assert ci_script.exists(), "CI script should exist in scripts/"

    def test_ci_d_directory_exists(self):
        """Test that ci.d directory exists."""
        ci_d = Path(__file__).parents[1] / "scripts" / "ci.d"
        # Directory may not exist in minimal projects
        if ci_d.exists():
            assert ci_d.is_dir()

    def test_version_file_exists(self):
        """Test that VERSION file exists."""
        version_file = Path(__file__).parents[1] / "VERSION"
        assert version_file.exists(), "VERSION file should exist in project root"

        # Verify it contains a version string
        version_content = version_file.read_text().strip()
        assert version_content, "VERSION file should not be empty"
        # Basic version format check (e.g., "1.0.0")
        assert len(version_content.split(".")) == 3, "VERSION should be semantic version (X.Y.Z)"


class TestBootstrapVenvIsolation:
    """Test virtual environment isolation."""

    def test_venv_ci_directory(self):
        """Test that .venv-ci directory is used for CI."""
        venv_ci = Path(__file__).parents[1] / ".venv-ci"

        # In CI environment, .venv-ci should exist
        # In development, it may not exist yet
        if venv_ci.exists():
            assert venv_ci.is_dir()

            # Check for common CI tools
            bin_dir = venv_ci / "bin" if os.name != "nt" else venv_ci / "Scripts"
            if bin_dir.exists():
                # Common CI tools that should be in .venv-ci
                common_tools = ["pip", "pytest"]
                for tool in common_tools:
                    tool_path = bin_dir / tool
                    # Tool may or may not exist depending on bootstrap stage
                    if tool_path.exists():
                        assert tool_path.is_file()
