# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import numpy as np
from collections.abc import Iterable
from numpy.typing import DTypeLike
from pathlib import Path
from typing import Any

MODEL_DATA_KEYS = (
    "pierside",
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
)


class AnalyseDataMixin:
    def initData(self) -> None:
        self.latitude: float = 0
        self.pierside: list[str] = []
        self.countSequence: np.ndarray = np.array([])
        self.errorIndex: np.ndarray = np.array([])
        self.scaleS: np.ndarray = np.array([])
        self.altitude: np.ndarray = np.array([])
        self.azimuth: np.ndarray = np.array([])
        self.errorAngle: np.ndarray = np.array([])
        self.errorRMS: np.ndarray = np.array([])
        self.errorRA_S: np.ndarray = np.array([])
        self.errorDEC_S: np.ndarray = np.array([])
        self.errorRA: np.ndarray = np.array([])
        self.errorDEC: np.ndarray = np.array([])
        self.angularPosRA: np.ndarray = np.array([])
        self.angularPosDEC: np.ndarray = np.array([])

    def writeGui(self, data: list[dict[str, Any]], loadFilePath: Path) -> None:
        d = data[0]
        de = data[-1]

        title = f"Analyse Model     {loadFilePath.stem}"
        self.setWindowTitle(title)
        self.ui.exposureTime.setText(f"{d.get('exposureTime', '')}")
        self.ui.solver.setText(d.get("plateSolveApp", ""))
        self.ui.binning.setText(f"{d.get('binning', 0):1.0f}")
        self.ui.time.setText(d.get("julianDate", "").replace("T", "  ").replace("Z", ""))
        self.ui.subframe.setText(f"{d.get('subFrame', 0):3.0f}")
        self.ui.modelTerms.setText(f"{d.get('modelTerms', 0):02.0f}")
        self.ui.modelErrorRMS.setText(f"{d.get('modelErrorRMS', 0):5.1f}")
        self.ui.modelOrthoError.setText(f"{d.get('modelOrthoError', 0):5.0f}")
        self.ui.modelPolarError.setText(f"{d.get('modelPolarError', 0):5.0f}")
        self.ui.focalLength.setText(f"{d.get('focalLength', 0):4.0f}")
        self.ui.profile.setText(f"{d.get('profile', '')}")
        self.ui.firmware.setText(f"{d.get('firmware', '')}")
        self.ui.totalPoints.setText(f"{d.get('lenSequence', 0)}")
        self.ui.goodPoints.setText(f"{de.get('errorIndex', 0)}")
        app = de.get("astrometryApp", "").split("-")[0].strip()
        self.ui.solver.setText(f"{app}")
        version = d.get("version", "").removeprefix("MountWizzard4 - v")
        self.ui.version.setText(f"{version}")

    @staticmethod
    def list2array(
        values: Iterable[Any], fill: float = 0.0, dtype: DTypeLike = np.float32
    ) -> np.ndarray:

        def cleanValue(v: Any) -> float:
            if v is None:
                return float(fill)
            try:
                f = float(v)
            except (OverflowError, TypeError, ValueError):
                return float(fill)
            if np.isnan(f):
                return float(fill)
            return f

        return np.array([cleanValue(v) for v in values], dtype=dtype)

    @staticmethod
    def validateModelData(modelJSON: Any) -> str | None:
        if not isinstance(modelJSON, list) or not modelJSON:
            return "model data must be a non-empty list of records"
        if any(not isinstance(record, dict) for record in modelJSON):
            return "each model data record must be an object"

        missingKeys = {key for record in modelJSON for key in MODEL_DATA_KEYS if key not in record}
        if missingKeys:
            return f"model data is missing required fields: {', '.join(sorted(missingKeys))}"
        if (
            "latitude" not in modelJSON[0]
            or not isinstance(modelJSON[0]["latitude"], (int, float))
            or isinstance(modelJSON[0]["latitude"], bool)
        ):
            return "model data must include a numeric latitude in its first record"
        return None

    def generateDataSets(self, modelJSON: list[dict[str, Any]]) -> None:
        model = {}
        for key in modelJSON[0]:
            model[key] = []
            for index in range(len(modelJSON)):
                model[key].append(modelJSON[index][key])

        self.latitude = modelJSON[0].get("latitude")
        self.pierside = model["pierside"]
        self.countSequence = self.list2array(model["countSequence"], dtype=np.int64)
        self.errorIndex = self.list2array(model["errorIndex"], dtype=np.int64) - 1
        self.scaleS = self.list2array(model["scaleS"], dtype=np.float32)
        self.altitude = self.list2array(model["altitude"], dtype=np.float32)
        self.azimuth = self.list2array(model["azimuth"], dtype=np.float32)
        self.errorAngle = self.list2array(model["errorAngle"], dtype=np.float32)
        self.errorRMS = self.list2array(model["errorRMS"], dtype=np.float32)
        self.errorRA_S = self.list2array(model["errorRA_S"], dtype=np.float32)
        self.errorDEC_S = self.list2array(model["errorDEC_S"], dtype=np.float32)
        self.errorRA = self.list2array(model["errorRA"], dtype=np.float32)
        self.errorDEC = self.list2array(model["errorDEC"], dtype=np.float32)
        self.angularPosRA = self.list2array(model["angularPosRA"], dtype=np.float32)
        self.angularPosDEC = self.list2array(model["angularPosDEC"], dtype=np.float32)

    def processModel(self, loadFilePath: Path) -> None:
        try:
            with open(loadFilePath) as infile:
                modelJSON = json.load(infile)
        except json.JSONDecodeError as e:
            self.log.warning("Cannot load model file: %s, error: %s", [loadFilePath], e)
            return

        validationError = self.validateModelData(modelJSON)
        if validationError is not None:
            self.log.warning("Cannot load model file: %s, error: %s", loadFilePath, validationError)
            return

        self.writeGui(modelJSON, loadFilePath)
        self.generateDataSets(modelJSON)
        self.drawAll()
