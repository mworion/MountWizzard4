############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
"""Tests for mw4.base.bootstrap utility functions."""

import mw4.base.bootstrap as bootstrap
import sys
import unittest.mock as mock


def test_namesImportable():
    """Every public camelCase name is importable from mw4.base.bootstrap."""
    from mw4.base.bootstrap import (
        configureEnvironment,
        exceptHook,
        extractDataFiles,
        minimizeStartTerminal,
        setupWorkDirs,
        writeSystemInfo,
    )

    assert callable(configureEnvironment)
    assert callable(exceptHook)
    assert callable(extractDataFiles)
    assert callable(minimizeStartTerminal)
    assert callable(setupWorkDirs)
    assert callable(writeSystemInfo)


def test_minimizeStartTerminalNonWindows():
    """minimizeStartTerminal is a no-op on non-Windows platforms."""
    with mock.patch("platform.system", return_value="Linux"):
        bootstrap.minimizeStartTerminal()  # must not raise


def test_minimizeStartTerminalOnWindows():
    """The Windows code path in minimizeStartTerminal calls ShowWindow."""
    mockCtypes = mock.MagicMock()
    with mock.patch("platform.system", return_value="Windows"):
        with mock.patch.dict(sys.modules, {"ctypes": mockCtypes}):
            bootstrap.minimizeStartTerminal()
    mockCtypes.windll.user32.ShowWindow.assert_called_once_with(
        mockCtypes.windll.kernel32.GetConsoleWindow(), 0
    )
