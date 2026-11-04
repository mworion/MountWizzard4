# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import logging
import numpy as np
from collections.abc import Iterable
from numpy.typing import DTypeLike, NDArray
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

        array = np.array(list(values), dtype=np.float64)
        if np.isinf(array).any():
            raise ValueError("Infinite plot values are not supported.")
        missing = np.isnan(array)
        if missing.any():
            logging.getLogger("MW4").warning(
                "Model plots: replacing %s legacy null/NaN values with %s.", missing.sum(), fill
            )
            array[missing] = fill
        return array.astype(dtype)

    def loadModel(self, loadFilePath: Path) -> list[dict[str, Any]] | None:
        try:
            with open(loadFilePath) as infile:
                modelJSON = json.load(infile)
        except (OSError, json.JSONDecodeError) as e:
            self.log.warning("Cannot load model file: %s, error: %s", loadFilePath, e)
            return None
        self.generateDataSets(modelJSON)
        return modelJSON

    def ascendingErrors(self) -> tuple[list[int], list[float], list[str]]:
        points = sorted(
            zip(self.errorRMS, self.errorIndex, self.pierside, strict=True),
            key=lambda point: point[0],
        )
        return (
            [int(point[1]) for point in points],
            [float(point[0]) for point in points],
            [point[2] for point in points],
        )

    def declinationErrors(self, errors: NDArray[np.float32]) -> list[float]:
        return [float(x if p == "W" else -x) for x, p in zip(errors, self.pierside, strict=True)]

    def generateDataSets(self, modelJSON: list[dict[str, Any]]) -> None:
        self.latitude = modelJSON[0]["latitude"]
        self.pierside = [record["pierside"] for record in modelJSON]
        self.countSequence = self.list2array(
            (record["countSequence"] for record in modelJSON), dtype=np.int64
        )
        self.errorIndex = (
            self.list2array((record["errorIndex"] for record in modelJSON), dtype=np.int64) - 1
        )
        self.scaleS = self.list2array(record["scaleS"] for record in modelJSON)
        self.altitude = self.list2array(record["altitude"] for record in modelJSON)
        self.azimuth = self.list2array(record["azimuth"] for record in modelJSON)
        self.errorAngle = self.list2array(record["errorAngle"] for record in modelJSON)
        self.errorRMS = self.list2array(record["errorRMS"] for record in modelJSON)
        self.errorRA_S = self.list2array(record["errorRA_S"] for record in modelJSON)
        self.errorDEC_S = self.list2array(record["errorDEC_S"] for record in modelJSON)
        self.errorRA = self.list2array(record["errorRA"] for record in modelJSON)
        self.errorDEC = self.list2array(record["errorDEC"] for record in modelJSON)
        self.angularPosRA = self.list2array(record["angularPosRA"] for record in modelJSON)
        self.angularPosDEC = self.list2array(record["angularPosDEC"] for record in modelJSON)
