# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import platform
from collections.abc import Callable

# The only place in mw4 that asks the operating system. All other modules use
# these constants, accessed as ``platformInfo.IS_WINDOWS`` so tests can patch them.
SYSTEM: str = platform.system()
IS_WINDOWS: bool = SYSTEM == "Windows"
IS_MAC: bool = SYSTEM == "Darwin"
IS_LINUX: bool = SYSTEM == "Linux"
EXE_SUFFIX: str = ".exe" if IS_WINDOWS else ""


def registerWindowsBackends[T](run: dict[str, T], factories: dict[str, Callable[[], T]]) -> None:
    """Add Windows-only back-ends (ASCOM, SGPro) to a device's run table. The
    factories are callables, because the back-end classes only exist on Windows.
    """
    if not IS_WINDOWS:
        return
    for name, factory in factories.items():
        run[name] = factory()
