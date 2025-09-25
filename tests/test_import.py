"""
Basic import tests for hyperlib.
"""

import pytest


def test_hyperlib_import():
    """Test that hyperlib can be imported."""
    import hyperlib
    assert hyperlib is not None


def test_submodules_import():
    """Test that submodules can be imported."""
    from hyperlib import config, logger, timeout, container
    
    assert config is not None
    assert logger is not None
    assert timeout is not None
    assert container is not None
