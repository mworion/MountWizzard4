# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import numpy as np
import pytest
from mw4.gui.extWindows.analyse.analyseData import AnalyseData
from pathlib import Path
from unittest import mock


@pytest.fixture(scope="module")
def function() -> AnalyseData:
    return AnalyseData()


def test_list2array(function: AnalyseData) -> None:
    values = [1.5, None, 3, float("nan"), "4.2", "x", {}, 10**4000]
    np.testing.assert_array_equal(
        function.list2array(values),
        np.array([1.5, 0, 3, 0, 4.2, 0, 0, 0], dtype=np.float32),
    )


def test_dataIsIndependent() -> None:
    data = AnalyseData()
    assert data.latitude == 0
    assert data.azimuth.size == 0
    assert not hasattr(data, "app")
    assert not hasattr(data, "ui")
    assert not hasattr(data, "parentWindow")
    assert not hasattr(data, "workerRebuildModel")


def test_loadModel(function: AnalyseData) -> None:
    path = Path("tests/testData/test.model")
    records = function.loadModel(path)
    assert records == json.loads(path.read_text())
    assert len(function.azimuth) == len(records)
    assert function.latitude == records[0]["latitude"]


@pytest.mark.parametrize(
    "error", [PermissionError("cannot read"), json.JSONDecodeError("invalid", "", 0)]
)
def test_loadFailure(function: AnalyseData, error: Exception) -> None:
    previous = function.azimuth
    with (
        mock.patch("builtins.open", side_effect=error),
        mock.patch.object(function.log, "warning") as warning,
        mock.patch.object(function, "generateDataSets") as generate,
    ):
        assert function.loadModel(Path("unreadable.model")) is None
    warning.assert_called_once()
    generate.assert_not_called()
    assert function.azimuth is previous


def test_generateDataSets(function: AnalyseData) -> None:
    records = json.loads(Path("tests/testData/test.model").read_text())
    function.generateDataSets(records)
    assert function.latitude == records[0]["latitude"]
    assert function.pierside == [record["pierside"] for record in records]
    for name in (
        "countSequence",
        "errorIndex",
        "scaleS",
        "altitude",
        "azimuth",
        "errorAngle",
        "errorRMS",
        "errorRA_S",
        "errorDEC_S",
        "errorRA",
        "errorDEC",
        "angularPosRA",
        "angularPosDEC",
    ):
        dtype = np.int64 if name in ("countSequence", "errorIndex") else np.float32
        expected = function.list2array([record[name] for record in records], dtype=dtype)
        if name == "errorIndex":
            expected -= 1
        np.testing.assert_array_equal(getattr(function, name), expected)
        assert getattr(function, name).dtype == dtype
