# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from collections.abc import Iterator
from contextlib import contextmanager
from mw4.base import platformInfo
from unittest import mock


@contextmanager
def patchPlatform(system: str) -> Iterator[None]:
    """Make mw4.base.platformInfo behave as if running on the given system."""
    with mock.patch.multiple(
        platformInfo,
        SYSTEM=system,
        IS_WINDOWS=system == "Windows",
        IS_MAC=system == "Darwin",
        IS_LINUX=system == "Linux",
        EXE_SUFFIX=".exe" if system == "Windows" else "",
    ):
        yield
