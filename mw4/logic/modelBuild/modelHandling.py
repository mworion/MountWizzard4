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
from skyfield.api import Star

# local packages
from mountcontrol.model import Model
from mountcontrol.alignStar import AlignStar


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


def buildAlignModel(model: list[dict]) -> list:
    """ """
    alignModel = list()
    for mPoint in model:
        mCoord = Star(mPoint["raJNowM"], mPoint["decJNowM"])
        sCoord = Star(mPoint["raJNowS"], mPoint["decJNowS"])
        sidereal = mPoint["siderealTime"]
        pierside = mPoint["pierside"]
        programmingPoint = AlignStar(mCoord, sCoord, sidereal, pierside)
        alignModel.append(programmingPoint)
    return alignModel


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

    if len(model) > 99:
        model = model[:99]
        return model, "Too many model points in files, cut of to 99"
    return model, "Model data loaded"
