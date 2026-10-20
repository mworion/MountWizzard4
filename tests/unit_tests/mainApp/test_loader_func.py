# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
"""Tests for mw4.base.bootstrap utility functions."""

import sys
from mw4.base import bootstrap
from tests.unit_tests.unitTestAddOns.platformStub import patchPlatform
from unittest import mock


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
    with patchPlatform("Linux"):
        bootstrap.minimizeStartTerminal()  # must not raise


def test_minimizeStartTerminalOnWindows():
    """The Windows code path in minimizeStartTerminal calls ShowWindow."""
    mockCtypes = mock.MagicMock()
    with (
        patchPlatform("Windows"),
        mock.patch.dict(sys.modules, {"ctypes": mockCtypes}),
    ):
        bootstrap.minimizeStartTerminal()
    mockCtypes.windll.user32.ShowWindow.assert_called_once_with(
        mockCtypes.windll.kernel32.GetConsoleWindow(), 0
    )
