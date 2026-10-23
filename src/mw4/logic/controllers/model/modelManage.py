# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import logging
from dataclasses import dataclass
from mw4.logic.controllers.model.modelRunSupport import (
    convertAngleToFloat,
    convertFloatToAngle,
    writeRetrofitData,
)
from mw4.mountcontrol.model import Model
from pathlib import Path

log = logging.getLogger("MW4")


@dataclass
class StarDeletion:
    success: bool
    number: int
    errorRMS: float

    def text(self) -> str:
        return f"Point: {self.number + 1:3.0f}, RMS of {self.errorRMS:5.1f} arcsec deleted."


def starCount(model: Model) -> int:
    return 0 if model.numberStars is None else model.numberStars


def deleteWorstStar(model: Model) -> StarDeletion:
    """Delete the star with the highest RMS error from the mount model."""
    worst = max(model.starList, key=lambda x: x.errorRMS)
    return StarDeletion(model.deletePoint(worst.number), worst.number, worst.errorRMS)


def isTargetReached(model: Model, targetRMS: float, overall: bool) -> bool:
    """Optimization is finished when the model (overall) or every single star
    (not overall) is below the target RMS.
    """
    if overall:
        return model.errorRMS < targetRMS
    return all(star.errorRMS < targetRMS for star in model.starList)


def writeOptimizedModel(
    fittedModelPath: Path, modelDir: Path, pointsOut: list[int], mountModel: Model
) -> Path:
    """Write the fitted model file without the removed points as '-opt' file.

    Returns the path of the new file, or the unchanged path if nothing was written.
    """
    if not pointsOut or fittedModelPath.is_dir():
        return fittedModelPath
    newName = fittedModelPath.stem.replace("-opt", "") + "-opt"
    newPath = modelDir / (newName + ".model")

    try:
        with open(fittedModelPath) as actFile:
            actModel = convertFloatToAngle(json.load(actFile))
    except json.JSONDecodeError as e:
        log.warning("Cannot load model file: %s, error: %s", [fittedModelPath], e)
        return fittedModelPath

    newModel = [element for element in actModel if element["errorIndex"] not in pointsOut]
    newModel = writeRetrofitData(mountModel, newModel)
    newModel = convertAngleToFloat(newModel)
    with open(newPath, "w+") as newFile:
        json.dump(newModel, newFile, sort_keys=True, indent=4)
    return newPath
