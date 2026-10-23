# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
from mw4.logic.controllers.model import modelManage
from mw4.logic.controllers.model.modelManage import (
    StarDeletion,
    deleteWorstStar,
    isTargetReached,
    starCount,
    writeOptimizedModel,
)
from mw4.mountcontrol.model import Model
from mw4.mountcontrol.modelStar import ModelStar
from pathlib import Path
from skyfield.api import Angle, Star
from unittest import mock


def makeModel(errors: list[float]) -> Model:
    model = Model(mock.MagicMock())
    model.starList = [
        ModelStar(Star(ra_hours=0, dec_degrees=0), err, Angle(degrees=0), number=i)
        for i, err in enumerate(errors)
    ]
    model.numberStars = len(errors)
    return model


def test_starDeletionText() -> None:
    assert StarDeletion(True, 2, 3.0).text() == "Point:   3, RMS of   3.0 arcsec deleted."


def test_starCount() -> None:
    model = Model(mock.MagicMock())
    model.numberStars = None
    assert starCount(model) == 0
    model.numberStars = 4
    assert starCount(model) == 4


def test_deleteWorstStar() -> None:
    model = makeModel([1.0, 5.0, 2.0])
    with mock.patch.object(model, "deletePoint", return_value=True) as delete:
        result = deleteWorstStar(model)
    delete.assert_called_once_with(1)
    assert result == StarDeletion(True, 1, 5.0)


def test_deleteWorstStar_failed() -> None:
    model = makeModel([1.0])
    with mock.patch.object(model, "deletePoint", return_value=False):
        assert not deleteWorstStar(model).success


def test_isTargetReached_overall() -> None:
    model = makeModel([1.0])
    model.errorRMS = 5
    assert isTargetReached(model, 10, True)
    assert not isTargetReached(model, 4, True)


def test_isTargetReached_single() -> None:
    model = makeModel([1.0, 8.0])
    assert isTargetReached(model, 10, False)
    assert not isTargetReached(model, 5, False)


def test_writeOptimizedModel_noPoints() -> None:
    path = Path("a-opt.model")
    assert writeOptimizedModel(path, Path(), [], Model(mock.MagicMock())) == path


def test_writeOptimizedModel_directory(tmp_path: Path) -> None:
    assert writeOptimizedModel(tmp_path, tmp_path, [1], Model(mock.MagicMock())) == tmp_path


def test_writeOptimizedModel_invalidJson(tmp_path: Path) -> None:
    path = tmp_path / "a.model"
    path.write_text("not json")
    assert writeOptimizedModel(path, tmp_path, [1], Model(mock.MagicMock())) == path


def test_writeOptimizedModel(tmp_path: Path) -> None:
    path = tmp_path / "a-opt.model"
    path.write_text("[]")
    with (
        mock.patch.object(
            modelManage, "convertFloatToAngle", return_value=[{"errorIndex": 1}, {"errorIndex": 3}]
        ),
        mock.patch.object(modelManage, "writeRetrofitData", side_effect=lambda m, x: x),
        mock.patch.object(modelManage, "convertAngleToFloat", side_effect=lambda x: x),
    ):
        newPath = writeOptimizedModel(path, tmp_path, [1], Model(mock.MagicMock()))
    assert newPath == tmp_path / "a-opt.model"
    assert json.loads(newPath.read_text()) == [{"errorIndex": 3}]
