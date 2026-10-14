"""Tests for the generated version metadata."""

import nhp._version as version_module


def test_version_module_exports():
    assert version_module.__version__
    assert version_module.version == version_module.__version__
    assert isinstance(version_module.__version_tuple__, tuple)
    assert version_module.version_tuple == version_module.__version_tuple__
    assert version_module.__commit_id__ is not None
    assert version_module.commit_id == version_module.__commit_id__
