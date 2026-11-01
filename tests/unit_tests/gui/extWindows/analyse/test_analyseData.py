# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import gc
import json
import numpy as np
import pytest
from mw4.gui.extWindows.analyse.analyseW import AnalyseWindow
from pathlib import Path
from PySide6.QtWidgets import QApplication
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    func = AnalyseWindow(app=makeApp(), title="Analyse")
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_writeGui_1(function):
    function.writeGui([{"a": 1}], Path("test"))


def test_list_to_array_replaces_none_and_nan(function):
    src = [1.5, None, 3, float("nan"), "4.2", "x"]
    arr = function.list2array(src, fill=0.0, dtype=np.float32)
    expected = np.array([1.5, 0.0, 3.0, 0.0, 4.2, 0.0], dtype=np.float32)
    for i, _item in enumerate(src):
        assert expected[i] == arr[i]


def test_list2array_handlesUnconvertibleValues(function):
    arr = function.list2array([{}, 10**4000])
    assert arr.tolist() == [0.0, 0.0]


def test_generateDataSets(function):
    with open("tests/testData/test.model") as infile:
        modelJSON = json.load(infile)

    function.generateDataSets(modelJSON)
    assert function.latitude == 48.1


def test_validateModelData(function):
    with open("tests/testData/test.model") as infile:
        validModel = json.load(infile)

    assert function.validateModelData(validModel) is None
    assert function.validateModelData({}) is not None
    assert function.validateModelData([None]) is not None
    assert function.validateModelData([{"latitude": 48.1}]) is not None

    noLatitude = [record.copy() for record in validModel]
    del noLatitude[0]["latitude"]
    assert function.validateModelData(noLatitude) is not None

    invalidLatitude = [record.copy() for record in validModel]
    invalidLatitude[0]["latitude"] = "48.1"
    assert function.validateModelData(invalidLatitude) is not None

    booleanLatitude = [record.copy() for record in validModel]
    booleanLatitude[0]["latitude"] = True
    assert function.validateModelData(booleanLatitude) is not None


def test_processModel_1(function):
    with (
        mock.patch.object(function, "writeGui"),
        mock.patch.object(function, "generateDataSets"),
        mock.patch.object(function, "drawAll"),
    ):
        function.processModel(Path("tests/testData/test.model"))


def test_processModel_2(function):
    with mock.patch.object(
        json, "load", return_value={}, side_effect=json.JSONDecodeError("test", "test", 0)
    ):
        function.processModel(Path("tests/testData/test.model"))


@pytest.mark.parametrize("modelJSON", [[], [{"latitude": 48.1}]])
def test_processModel_invalidData(function, modelJSON):
    with (
        mock.patch.object(json, "load", return_value=modelJSON),
        mock.patch.object(function.log, "warning") as warning,
        mock.patch.object(function, "writeGui") as writeGui,
        mock.patch.object(function, "generateDataSets") as generateDataSets,
    ):
        function.processModel(Path("tests/testData/test.model"))

    warning.assert_called_once()
    writeGui.assert_not_called()
    generateDataSets.assert_not_called()
