# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.appSignals import (
    AppSignals,
    HemisphereSignals,
    ModelSignals,
    SystemSignals,
    UiSignals,
)
from pathlib import Path
from PySide6.QtCore import QObject
from unittest import mock


def test_groupClasses():
    signals = AppSignals()
    assert isinstance(signals.ui, UiSignals)
    assert isinstance(signals.hemisphere, HemisphereSignals)
    assert isinstance(signals.model, ModelSignals)
    assert isinstance(signals.system, SystemSignals)
    for group in (signals.ui, signals.hemisphere, signals.model, signals.system):
        assert isinstance(group, QObject)


def test_uiSignals():
    ui = AppSignals().ui
    slot = mock.Mock()
    ui.msg.connect(slot)
    ui.msg.emit(1, "a", "b", "c")
    slot.assert_called_once_with(1, "a", "b", "c")

    slot = mock.Mock()
    ui.showImage.connect(slot)
    ui.showImage.emit(Path("image.fits"))
    slot.assert_called_once_with(Path("image.fits"))


def test_hemisphereSignals():
    hemisphere = AppSignals().hemisphere
    slot = mock.Mock()
    hemisphere.redrawHemisphere.connect(slot)
    hemisphere.redrawHemisphere.emit()
    slot.assert_called_once_with()


def test_modelSignals():
    model = AppSignals().model
    slot = mock.Mock()
    model.sendSatelliteData.connect(slot)
    model.sendSatelliteData.emit(1, 2)
    slot.assert_called_once_with(1, 2)


def test_systemSignals():
    system = AppSignals().system
    slot = mock.Mock()
    system.parkChanged.connect(slot)
    system.parkChanged.emit()
    slot.assert_called_once_with()
