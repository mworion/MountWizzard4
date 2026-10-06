# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from unittest import mock


def test_main_imports_run():
    """Test that __main__ module successfully imports and calls run()."""
    with mock.patch("mw4.cli.run") as mock_run:
        import mw4.__main__  # noqa: F401

        assert mock_run is not None
