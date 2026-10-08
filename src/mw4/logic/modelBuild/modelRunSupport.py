# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import json
import logging
from datetime import datetime
from mw4.mountcontrol.model import Model
from pathlib import Path
from skyfield.api import Angle, load
from typing import Any

log = logging.getLogger("MW4")
ts = load.timescale()

hourAngles = ["raJNowM", "raJNowS", "raJ2000M", "raJ2000S", "siderealTime", "haMountModel"]
degreeAngles = [
    "decJNowM",
    "decJNowS",
    "decJ2000M",
    "decJ2000S",
    "altitude",
    "azimuth",
    "angularPosRA",
    "angularPosDEC",
    "modelOrthoError",
    "modelPolarError",
    "errorAngle",
    "errorDEC",
    "errorDEC_S",
    "errorRA",
    "errorRA_S",
    "decMountModel",
    "angleS",
]


def writeRetrofitData(mountModel: Model, buildModel: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for i, mPoint in enumerate(buildModel):
        mPoint["errorRMS"] = mountModel.starList[i].errorRMS
        mPoint["errorAngle"] = mountModel.starList[i].errorAngle
        mPoint["haMountModel"] = mountModel.starList[i].coord.ra
        mPoint["decMountModel"] = mountModel.starList[i].coord.dec
        mPoint["errorRA"] = mountModel.starList[i].errorRA()
        mPoint["errorDEC"] = mountModel.starList[i].errorDEC()
        mPoint["errorIndex"] = mountModel.starList[i].number
        mPoint["modelTerms"] = mountModel.terms
        mPoint["modelErrorRMS"] = mountModel.errorRMS
        mPoint["modelOrthoError"] = mountModel.orthoError
        mPoint["modelPolarError"] = mountModel.polarError
    return buildModel


def convertFloatToAngle(model: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for mPoint in model:
        for key in mPoint:
            if key in hourAngles:
                mPoint[key] = Angle(hours=mPoint[key])
            elif key in degreeAngles:
                mPoint[key] = Angle(degrees=mPoint[key])
            elif key == "julianDate":
                mPoint[key] = ts.from_datetime(datetime.fromisoformat(mPoint[key]))
            elif key == "imagePath":
                mPoint[key] = Path(mPoint[key])
    return model


def convertAngleToFloat(model: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for mPoint in model:
        for key in mPoint:
            if key in hourAngles:
                mPoint[key] = mPoint[key].hours
            elif key in degreeAngles:
                mPoint[key] = mPoint[key].degrees
            elif key == "julianDate":
                mPoint[key] = mPoint[key].utc_iso()
            elif key == "imagePath":
                mPoint[key] = str(mPoint[key])
    return model


def buildSaveData(
    buildData: dict[str, dict[str, Any]], meta: dict[str, Any], mountModel: Model
) -> list[dict[str, Any]] | None:
    saveData = [dict(item) | meta for item in buildData.values() if item["success"]]
    if len(mountModel.starList) != len(saveData):
        log.warning("Error in model data: difference in length")
        return None
    return convertAngleToFloat(writeRetrofitData(mountModel, saveData))


def saveModelFile(modelPath: Path, saveData: list[dict[str, Any]]) -> None:
    log.debug(f"{'Save model':15s}: Len: [{len(saveData)}]")
    with open(modelPath, "w") as outfile:
        json.dump(saveData, outfile, sort_keys=True, indent=4)


def loadModelsFromFile(modelFilesPath: list[Path]) -> tuple[dict[str, dict[str, Any]], str]:
    model = {}
    modelLoad = []
    for path in modelFilesPath:
        if not path.is_file():
            return model, f"File {path} does not exist"

        try:
            with open(path) as infile:
                model_part = json.load(infile)
                modelLoad += model_part
        except json.JSONDecodeError:
            errText = f"Cannot load model json file: {path.name}"
            log.warning(errText)
            return model, errText

    for i, mPoint in enumerate(convertFloatToAngle(modelLoad)[:99]):
        model[f"point-{i:03d}"] = mPoint
    if len(modelLoad) > 99:
        return model, "Too many model points in files, cut of to 99"
    return model, "Model data loaded"


def findKeysSourceInDest(buildModel: list[dict], refModel: list[dict]) -> tuple[list, list]:
    pointsIn = []
    pointsOut = []
    for buildPoint in buildModel:
        for mountPoint in refModel:
            dHA = refModel[mountPoint]["ha"] - buildModel[buildPoint]["ha"]
            dDEC = refModel[mountPoint]["dec"] - buildModel[buildPoint]["dec"]

            fitHA = abs(dHA) < 1e-4
            fitDEC = abs(dDEC) < 1e-4

            if fitHA and fitDEC:
                pointsIn.append(buildPoint)
                break

        else:
            pointsOut.append(buildPoint)
    return pointsIn, pointsOut


def generateFileModelData(fileModel: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    fileModelData = {}

    for star in fileModel:
        index = star.get("errorIndex", 0)
        mount = {
            "ha": star.get("haMountModel", 0),
            "dec": star.get("decMountModel", 0),
        }
        fileModelData[index] = mount

    return fileModelData


def generateMountModelData(mountModel: Model) -> dict[int, dict[str, float]]:
    mountModelData = {}

    for star in mountModel.starList:
        mountModelData[star.number] = {
            "ha": star.coord.ra.hours,
            "dec": star.coord.dec.degrees,
        }

    return mountModelData


def compareFile(
    modelFilePath: Path, mountModelData: dict[int, dict[str, float]]
) -> tuple[list, list]:
    pointsIn = []
    pointsOut = []

    with open(modelFilePath) as inFile:
        try:
            fileModel = json.load(inFile)
            fileModelData = generateFileModelData(fileModel)
        except json.JSONDecodeError as e:
            log.warning(f"{'Cannot load':15s}: model file [{[inFile]}], error: {e}")
        else:
            pointsIn, pointsOut = findKeysSourceInDest(fileModelData, mountModelData)

    return pointsIn, pointsOut


def findFittingModel(mountModel: Model, modelPath: Path) -> tuple[Path, list]:
    mountModelData = generateMountModelData(mountModel)
    fittedModelPath = Path()

    pointsOut = []
    for modelFilePath in sorted(modelPath.glob("*.model"), key=lambda x: x.stem):
        pointsIn, pointsOut = compareFile(modelFilePath, mountModelData)
        fileCount = len(pointsIn) + len(pointsOut)
        mountCount = len(mountModelData)
        isModel = len(pointsIn) >= 3
        isNotLarger = fileCount <= mountCount
        isOverlapping = mountCount - len(pointsIn) <= 3
        if isModel and isNotLarger and isOverlapping:
            fittedModelPath = modelFilePath
            break

    return fittedModelPath, pointsOut
