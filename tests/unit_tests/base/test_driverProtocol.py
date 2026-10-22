# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.driverProtocol import HasDriverConfig, HasSignals
from types import SimpleNamespace


def test_HasSignals():
    assert isinstance(SimpleNamespace(signals=1), HasSignals)
    assert not isinstance(SimpleNamespace(), HasSignals)


def test_HasDriverConfig():
    assert isinstance(SimpleNamespace(config=1), HasDriverConfig)
    assert not isinstance(SimpleNamespace(), HasDriverConfig)
