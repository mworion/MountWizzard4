############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import json
from pathlib import Path
from datetime import datetime

# external packages
from skyfield.api import Angle, load

# local packages
from mountcontrol.model import Model


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
]


def writeRetrofitData(mountModel: Model, buildModel: list[dict]) -> dict:
    """ """
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


def convertFloatToAngle(model: list[dict]) -> list[dict]:
    """ """
    for mPoint in model:
        for key in mPoint.keys():
            if key in hourAngles:
                mPoint[key] = Angle(hours=mPoint[key])
            elif key in degreeAngles:
                mPoint[key] = Angle(degrees=mPoint[key])
            elif key == "julianDate":
                mPoint[key] = ts.from_datetime(datetime.fromisoformat(mPoint[key]))
    return model


def convertAngleToFloat(model: list[dict]) -> list[dict]:
    """ """
    for mPoint in model:
        for key in mPoint.keys():
            if key in hourAngles:
                mPoint[key] = mPoint[key].hours
            elif key in degreeAngles:
                mPoint[key] = mPoint[key].degrees
            elif key == "julianDate":
                mPoint[key] = mPoint[key].utc_iso()
    return model


def loadModelsFromFile(modelFilesPath: list[Path]) -> (list[dict], str):
    """ """
    model = []
    for path in modelFilesPath:
        if not path.is_file():
            return [], f"File {path} does not exist"

        try:
            with open(path, "r") as infile:
                model_part = json.load(infile)
                model += model_part
        except Exception:
            errText = f"Cannot load model json file: {path.name}"
            log.warning(errText)
            return [], errText

    model = convertFloatToAngle(model)

    if len(model) > 99:
        model = model[:99]
        return model, "Too many model points in files, cut of to 99"
    return model, "Model data loaded"


def findKeysFromSourceInDest(buildModel: list[dict], refModel: list[dict]) -> (list, list):
    """ """
    pointsIn = []
    pointsOut = []
    for buildPoint in buildModel:
        for mountPoint in refModel:
            dHA = refModel[mountPoint]["ha"] - buildModel[buildPoint]["ha"]
            dHA = dHA / refModel[mountPoint]["ha"]
            dDEC = refModel[mountPoint]["dec"] - buildModel[buildPoint]["dec"]
            dDEC = dDEC / refModel[mountPoint]["dec"]

            fitHA = abs(dHA) < 1e-4
            fitDEC = abs(dDEC) < 1e-4

            if fitHA and fitDEC:
                pointsIn.append(buildPoint)
                break

        else:
            pointsOut.append(buildPoint)
    return pointsIn, pointsOut


def generateFileModelData(fileModel: Model) -> dict:
    """"""
    fileModelData = {}

    for star in fileModel:
        index = star.get("errorIndex", 0)
        mount = {
            "ha": star.get("haMountModel", 0),
            "dec": star.get("decMountModel", 0),
        }
        fileModelData[index] = mount

    return fileModelData


def generateMountModelData(mountModel: Model) -> dict:
    """ """
    mountModelData = {}

    for star in mountModel.starList:
        mountModelData[star.number] = {
            "ha": star.coord.ra.hours,
            "dec": star.coord.dec.degrees,
        }

    return mountModelData


def compareFile(modelFilePath: Path, mountModelData: dict) -> (list, list):
    """ """
    pointsIn = []
    pointsOut = []

    with open(modelFilePath, "r") as inFile:
        try:
            fileModel = json.load(inFile)
            fileModelData = generateFileModelData(fileModel)
        except Exception as e:
            log.warning(f"Cannot load model file: {[inFile]}, error: {e}")
        else:
            pointsIn, pointsOut = findKeysFromSourceInDest(fileModelData, mountModelData)

    return pointsIn, pointsOut


def findFittingModel(mountModel: Model, modelPath: Path) -> (Path, list):
    """ """
    mountModelData = generateMountModelData(mountModel)
    fittedModelPath = Path()

    pointsOut = []
    for modelFilePath in sorted(modelPath.glob("*.model"), key=lambda x: x.stem):
        pointsIn, pointsOut = compareFile(modelFilePath, mountModelData)
        if len(pointsIn) > 2:
            fittedModelPath = modelFilePath
            break

    return fittedModelPath, pointsOut
