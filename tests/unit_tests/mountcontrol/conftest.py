# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.mountcontrol.mount import DeviceConfigMount
from mw4.mountcontrol.mountSignals import MountSignals
from pathlib import Path
from PySide6.QtCore import QThreadPool
from tests.unit_tests.unitTestAddOns.mountStubs import MountObsSite
from types import SimpleNamespace
from unittest import mock


@pytest.fixture(scope="module")
def mountContext() -> SimpleNamespace:
    """Minimal object satisfying the MountContext protocol."""
    return SimpleNamespace(
        config=DeviceConfigMount(),
        loggingTrace=False,
        mountIsUp=False,
        signals=MountSignals(),
        obsSite=MountObsSite(),
        firmware=mock.MagicMock(),
        threadPool=QThreadPool(),
        pathToData=Path("tests/work/data"),
        domeConfig={},
        updateDomeSettings=mock.MagicMock(),
    )
