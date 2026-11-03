# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import logging
import numpy as np
from collections.abc import Iterable
from numpy.typing import DTypeLike
from pathlib import Path
from typing import Any


class AnalyseData:
    def __init__(self) -> None:
        self.log = logging.getLogger("MW4")
        self.latitude: float = 0
        self.pierside: list[str] = []
        self.countSequence = np.array([])
        self.errorIndex = np.array([])
        self.scaleS = np.array([])
        self.altitude = np.array([])
        self.azimuth = np.array([])
        self.errorAngle = np.array([])
        self.errorRMS = np.array([])
        self.errorRA_S = np.array([])
        self.errorDEC_S = np.array([])
        self.errorRA = np.array([])
        self.errorDEC = np.array([])
        self.angularPosRA = np.array([])
        self.angularPosDEC = np.array([])

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

    def loadModel(self, loadFilePath: Path) -> list[dict[str, Any]] | None:
        try:
            with open(loadFilePath) as infile:
                modelJSON = json.load(infile)
        except (OSError, json.JSONDecodeError) as e:
            self.log.warning("Cannot load model file: %s, error: %s", loadFilePath, e)
            return None
        self.generateDataSets(modelJSON)
        return modelJSON

    def generateDataSets(self, modelJSON: list[dict[str, Any]]) -> None:
        model = {}
        for key in modelJSON[0]:
            model[key] = []
            for index in range(len(modelJSON)):
                model[key].append(modelJSON[index][key])

        self.latitude = modelJSON[0]["latitude"]
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
