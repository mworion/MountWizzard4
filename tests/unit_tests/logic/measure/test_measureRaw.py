# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.logic.measure.measureRaw import MeasureDataRaw
from typing import ClassVar
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function():
    class Test1:
        CYCLE_UPDATE_TASK: ClassVar = 1000
        data: ClassVar = {}

        @staticmethod
        def measureTask():
            return True

    func = MeasureDataRaw(app=mock.MagicMock(), parent=Test1())
    yield func


def test_startCommunication(function):
    with mock.patch.object(function.timerTask, "start"):
        function.startCommunication()


def test_stopCommunication(function):
    with mock.patch.object(function.timerTask, "stop"):
        function.stopCommunication()


def test_measureTask(function):
    function.measureTask()
