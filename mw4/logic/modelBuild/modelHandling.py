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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import json
from pathlib import Path

# external packages
from skyfield.api import Star, Angle

# local packages
from mountcontrol.model import Model
from mountcontrol.progStar import ProgStar


log = logging.getLogger("MW4")


def writeRetrofitData(alignModel: Model, buildModel: list[dict]) -> dict:
    """ """
    for i, mPoint in enumerate(buildModel):
        mPoint["errorRMS"] = alignModel.starList[i].errorRMS
        mPoint["errorAngle"] = alignModel.starList[i].errorAngle
        mPoint["haMountModel"] = alignModel.starList[i].coord.ra
        mPoint["decMountModel"] = alignModel.starList[i].coord.dec
        mPoint["errorRA"] = alignModel.starList[i].errorRA()
        mPoint["errorDEC"] = alignModel.starList[i].errorDEC()
        mPoint["errorIndex"] = alignModel.starList[i].number
        mPoint["modelTerms"] = alignModel.terms
        mPoint["modelErrorRMS"] = alignModel.errorRMS
        mPoint["modelOrthoError"] = alignModel.orthoError
        mPoint["modelPolarError"] = alignModel.polarError
    return buildModel


def buildProgModel(model: list[dict]) -> list:
    """ """
    progModel = list()
    for mPoint in model:
        mCoord = Star(mPoint["raJNowM"], mPoint["decJNowM"])
        sCoord = Star(mPoint["raJNowS"], mPoint["decJNowS"])
        sidereal = mPoint["siderealTime"]
        pierside = mPoint["pierside"]
        programmingPoint = ProgStar(mCoord, sCoord, sidereal, pierside)
        progModel.append(programmingPoint)
    return progModel


def convertFloatToAngle(model: list[dict]) -> list[dict]:
    """ """
    hourAngles = ["raJNowM", "raJNowS", "siderealTime", "haMountModel"]
    degreeAngles = [
        "decJNowM",
        "decJNowS",
        "altitude",
        "azimuth",
        "angularPosRA",
        "angularPosDEC",
        "modelOrthoError",
        "modelPolarError",
        "errorAngle",
        "decMountModel",
    ]

    for mPoint in model:
        for key in mPoint.keys():
            if key in hourAngles:
                mPoint[key] = Angle(hours=mPoint[key])
            elif key in degreeAngles:
                mPoint[key] = Angle(degrees=mPoint[key])
    return model


def convertAngleToFloat(model: list[dict]) -> list[dict]:
    """ """
    hourAngles = ["raJNowM", "raJNowS", "siderealTime", "haMountModel"]
    degreeAngles = [
        "decJNowM",
        "decJNowS",
        "altitude",
        "azimuth",
        "angularPosRA",
        "angularPosDEC",
        "modelOrthoError",
        "modelPolarError",
        "errorAngle",
        "decMountModel",
    ]

    for mPoint in model:
        for key in mPoint.keys():
            if key in hourAngles:
                mPoint[key] = mPoint[key].hours
            elif key in degreeAngles:
                mPoint[key] = mPoint[key].degrees
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
