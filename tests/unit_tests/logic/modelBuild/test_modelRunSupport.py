# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import json
import mw4.logic.modelBuild.modelRunSupport
import shutil
from datetime import datetime
from mw4.logic.modelBuild.modelRunSupport import (
    buildSaveData,
    compareFile,
    convertAngleToFloat,
    convertFloatToAngle,
    findFittingModel,
    findKeysSourceInDest,
    generateFileModelData,
    generateMountModelData,
    loadModelsFromFile,
    saveModelFile,
    writeRetrofitData,
)
from mw4.mountcontrol import obsSite
from mw4.mountcontrol.model import Model, ModelStar
from pathlib import Path
from skyfield.api import Angle, Star, load, wgs84
from typing import ClassVar
from unittest import mock

obsSite.location = wgs84.latlon(latitude_degrees=0, longitude_degrees=0, elevation_m=0)


def test_writeRetrofitData_1():
    class Parent:
        host = None

    mountModel = Model(parent=Parent())

    val = writeRetrofitData(mountModel, [])
    assert val == []


def test_writeRetrofitData_2():
    class Parent:
        host = None

    mountModel = Model(parent=Parent())
    p1 = Angle(hours=12)
    p2 = Angle(degrees=56)
    p3 = 1234.5
    p4 = Angle(degrees=90)
    modelStar1 = ModelStar(Star(ra=p1, dec=p2), p3, p4, number=1)

    mountModel.addStar(modelStar1)
    buildModel = [{"test": 1}]

    val = writeRetrofitData(mountModel, buildModel)
    assert "errorRMS" in val[0]
    assert "modelPolarError" in val[0]


def test_writeRetrofitData_3():
    class Parent:
        host = None

    mountModel = Model(parent=Parent())
    p1 = Angle(hours=121)
    p2 = Angle(degrees=56)
    p3 = 1234.5
    p4 = Angle(degrees=90)
    modelStar1 = ModelStar(Star(ra=p1, dec=p2), p3, p4, number=1)

    mountModel.addStar(modelStar1)
    buildModel = [{"errorRMS": 1}]

    val = writeRetrofitData(mountModel, buildModel)
    assert val[0]["errorRMS"] == 1234.5
    assert val[0]["errorRA"].degrees == Angle(degrees=1234.5).degrees


def test_convertFloatToAngle_1():
    [
        {
            "altitude": Angle(degrees=44.556745182012854),
            "azimuth": Angle(degrees=37.194805194805184),
            "binning": 1.0,
            "countSequence": 0,
            "decJNowS": Angle(degrees=64.3246),
            "decJNowM": Angle(degrees=64.32841185357267),
            "errorDEC": Angle(degrees=-229.0210134131381),
            "errorRMS": 237.1,
            "errorRA": Angle(degrees=-61.36599559380768),
            "exposureTime": 3.0,
            "fastReadout": True,
            "julianDate": "2019-06-08T08:57:57Z",
            "name": "m-file-2019-06-08-08-57-44",
            "lenSequence": 3,
            "imagePath": "/Users/mw/PycharmProjects/MountWizzard4/image/m-file-2019-06-08-08"
            "-57-44/image-000.fits",
            "pierside": "W",
            "raJNowS": Angle(hours=8.42882),
            "raJNowM": Angle(hours=8.427692953132278),
            "siderealTime": Angle(hours=12.5),
            "subFrame": 100.0,
        },
    ]

    model = [
        {
            "altitude": 44.556745182012854,
            "azimuth": 37.194805194805184,
            "binning": 1.0,
            "countSequence": 0,
            "decJNowS": 64.3246,
            "decJNowM": 64.32841185357267,
            "errorDEC": -229.0210134131381,
            "errorRMS": 237.1,
            "errorRA": -61.36599559380768,
            "exposureTime": 3.0,
            "fastReadout": True,
            "julianDate": "2019-06-08T08:57:57Z",
            "name": "m-file-2019-06-08-08-57-44",
            "lenSequence": 3,
            "imagePath": Path(
                "/Users/mw/PycharmProjects/MountWizzard4/image/m-file-2019-06-08-08-57-44/image-000.fits"
            ),
            "pierside": "W",
            "raJNowS": 8.42882,
            "raJNowM": 8.427692953132278,
            "siderealTime": 12.5,
            "subFrame": 100.0,
        },
    ]

    alignModel = convertFloatToAngle(model)
    assert isinstance(alignModel[0]["decJNowS"], Angle)
    assert isinstance(alignModel[0]["raJNowS"], Angle)
    assert isinstance(alignModel[0]["imagePath"], Path)


def test_convertAngleToFloat_1():
    ts = load.timescale()
    target = [
        {
            "altitude": Angle(degrees=44.556745182012854),
            "azimuth": Angle(degrees=37.194805194805184),
            "binning": 1.0,
            "countSequence": 0,
            "decJNowS": Angle(degrees=64.3246),
            "decJNowM": Angle(degrees=64.32841185357267),
            "errorDEC": Angle(degrees=-229.0210134131381),
            "errorRMS": 237.1,
            "errorRA": Angle(degrees=-61.36599559380768),
            "exposureTime": 3.0,
            "fastReadout": True,
            "julianDate": ts.from_datetime(datetime.fromisoformat("2019-06-08T08:57:57Z")),
            "name": "m-file-2019-06-08-08-57-44",
            "lenSequence": 3,
            "imagePath": "/Users/mw/PycharmProjects/MountWizzard4/image/m-file-2019-06-08-08"
            "-57-44/image-000.fits",
            "pierside": "W",
            "raJNowS": Angle(hours=8.42882),
            "raJNowM": Angle(hours=8.427692953132278),
            "siderealTime": Angle(hours=12.5),
            "subFrame": 100.0,
        },
    ]

    jsonModel = convertAngleToFloat(target)
    assert isinstance(jsonModel[0]["decJNowS"], float)
    assert isinstance(jsonModel[0]["raJNowS"], float)
    assert isinstance(jsonModel[0]["imagePath"], str)


def test_buildSaveData_1():
    mountModel = mock.MagicMock()
    mountModel.starList = [1, 2]
    buildData = {
        "im-00": {"success": True, "altitude": Angle(degrees=1), "a": 1},
        "im-01": {"success": False, "altitude": Angle(degrees=2)},
        "im-02": {"success": True, "altitude": Angle(degrees=3), "version": "old"},
    }
    meta = {"version": "1.0", "profile": "p"}
    with mock.patch.object(
        mw4.logic.modelBuild.modelRunSupport, "writeRetrofitData", side_effect=lambda m, d: d
    ):
        result = buildSaveData(buildData, meta, mountModel)
    assert len(result) == 2
    assert result[0]["version"] == "1.0"
    assert result[1]["version"] == "1.0"
    assert result[0]["profile"] == "p"
    assert result[0]["altitude"] == 1.0
    assert isinstance(buildData["im-00"]["altitude"], Angle)
    assert "profile" not in buildData["im-00"]


def test_buildSaveData_2():
    mountModel = mock.MagicMock()
    mountModel.starList = [1]
    buildData = {"im-00": {"success": True}, "im-01": {"success": True}}
    assert buildSaveData(buildData, {}, mountModel) is None


def test_saveModelFile_1(tmp_path):
    modelPath = tmp_path / "test.model"
    saveModelFile(modelPath, [{"a": 1}])
    assert json.loads(modelPath.read_text()) == [{"a": 1}]


def test_loadModelsFromFile_1():
    modelFilesPath = [Path()]
    model, msg = loadModelsFromFile(modelFilesPath)
    assert model == {}
    assert msg == "File . does not exist"


def test_loadModelsFromFile_2():
    shutil.copy("tests/testData/test.model", "tests/work/model/test.model")
    modelFilesPath = [Path("tests/work/model/test.model")]
    model, msg = loadModelsFromFile(modelFilesPath)
    assert len(model) == 58
    assert "point-000" in model
    assert "point-057" in model
    assert msg == "Model data loaded"


def test_loadModelsFromFile_3():
    shutil.copy("tests/testData/astrometry.cfg", "tests/work/model/test.model")
    modelFilesPath = [Path("tests/work/model/test.model")]
    model, msg = loadModelsFromFile(modelFilesPath)
    assert len(model) == 0
    assert msg == "Cannot load model json file: test.model"


def test_loadModelsFromFile_4():
    shutil.copy("tests/testData/test.model", "tests/work/model/test.model")
    shutil.copy("tests/testData/test1.model", "tests/work/model/test1.model")
    modelFilesPath = [
        Path("tests/work/model/test.model"),
        Path("tests/work/model/test1.model"),
    ]
    model, msg = loadModelsFromFile(modelFilesPath)
    assert len(model) == 99
    assert msg == "Too many model points in files, cut of to 99"
    assert isinstance(model["point-000"]["raJNowM"], Angle)


def test_findKeysFromSourceInDest_1():
    val1, val2 = findKeysSourceInDest({}, {})
    assert val1 == []
    assert val2 == []


def test_findKeysFromSourceInDest_2():
    source = {1: {"ha": 1, "dec": 2}, 2: {"ha": 4, "dec": 3}}
    dest = {1: {"ha": 2, "dec": 1}, 2: {"ha": 3, "dec": 4}}
    val1, val2 = findKeysSourceInDest(source, dest)
    assert val1 == []
    assert 1 in val2
    assert 2 in val2


def test_findKeysFromSourceInDest_3():
    source = {1: {"ha": 1, "dec": 2}, 2: {"ha": 3, "dec": 4}}
    dest = {1: {"ha": 2, "dec": 1}, 2: {"ha": 3, "dec": 4}}
    val1, val2 = findKeysSourceInDest(source, dest)
    assert 2 in val1
    assert 1 in val2


def test_findKeysFromSourceInDest_4():
    source = {1: {"ha": 0, "dec": 0}, 2: {"ha": 0.001, "dec": 0}}
    dest = {1: {"ha": 0, "dec": 0}}
    val1, val2 = findKeysSourceInDest(source, dest)
    assert val1 == [1]
    assert val2 == [2]


def test_generateFileModelData_1():
    model = [
        {
            "errorIndex": 1,
            "haMountModel": 10,
            "decMountModel": 20,
        },
        {
            "errorIndex": 2,
            "haMountModel": 30,
            "decMountModel": 40,
        },
    ]

    val = generateFileModelData(model)
    assert val != {}


def test_generateMountModelData_1():
    class ModelStar:
        number = 1
        coord = Star(ra_hours=10, dec_degrees=20)

    class Model:
        starList: ClassVar = [ModelStar(), ModelStar()]

    model = Model()
    val = generateMountModelData(model)
    assert val != {}


def test_compareFile_1():
    with mock.patch.object(json, "load", side_effect=json.JSONDecodeError("test", "test", 0)):
        val1, val2 = compareFile(Path("tests/testData/test.model"), {})
        assert val1 == []
        assert val2 == []


def test_compareFile_2():
    valIn, valOut = compareFile(Path("tests/testData/test.model"), {})
    assert len(valIn) == 0
    assert len(valOut) == 58


def test_findFittingModel_1():
    mountData = {i: {} for i in range(5)}
    with mock.patch.object(
        mw4.logic.modelBuild.modelRunSupport, "generateMountModelData", return_value=mountData
    ):
        with mock.patch.object(
            mw4.logic.modelBuild.modelRunSupport, "compareFile", return_value=([1, 2, 3], [4])
        ):
            filePath, pointsOut = findFittingModel({}, Path("tests/testData"))
        assert pointsOut == [4]
        assert filePath == Path("tests/testData/test.model")


def runFindFittingModel(mountCount, pointsIn, pointsOut):
    mountData = {i: {} for i in range(mountCount)}
    with (
        mock.patch.object(
            mw4.logic.modelBuild.modelRunSupport,
            "generateMountModelData",
            return_value=mountData,
        ),
        mock.patch.object(
            mw4.logic.modelBuild.modelRunSupport,
            "compareFile",
            return_value=(pointsIn, pointsOut),
        ),
    ):
        return findFittingModel({}, Path("tests/testData"))


def test_findFittingModel_2():
    filePath, pointsOut = runFindFittingModel(5, [1], [4])
    assert pointsOut == [4]
    assert filePath == Path()


def test_findFittingModel_3():
    filePath, pointsOut = runFindFittingModel(5, [1, 2, 3, 4, 5], [6])
    assert pointsOut == [6]
    assert filePath == Path()


def test_findFittingModel_4():
    filePath, pointsOut = runFindFittingModel(8, [1, 2, 3, 4], [])
    assert pointsOut == []
    assert filePath == Path()


def test_findFittingModel_5():
    filePath, _ = runFindFittingModel(6, [1, 2, 3], [])
    assert filePath == Path("tests/testData/test.model")
