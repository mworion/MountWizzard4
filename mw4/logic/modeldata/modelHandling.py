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

# external packages

# local packages

def writeRetrofitData(mountModel, buildModel):
    """
    :param mountModel:
    :param buildModel:
    :return:
    """
    for i, mPoint in enumerate(buildModel):
        mPoint['errorRMS'] = mountModel.starList[i].errorRMS
        mPoint['errorAngle'] = mountModel.starList[i].errorAngle
        mPoint['haMountModel'] = mountModel.starList[i].coord.ra
        mPoint['decMountModel'] = mountModel.starList[i].coord.dec
        mPoint['errorRA'] = mountModel.starList[i].errorRA()
        mPoint['errorDEC'] = mountModel.starList[i].errorDEC()
        mPoint['errorIndex'] = mountModel.starList[i].number
        mPoint['modelTerms'] = mountModel.terms
        mPoint['modelErrorRMS'] = mountModel.errorRMS
        mPoint['modelOrthoError'] = mountModel.orthoError
        mPoint['modelPolarError'] = mountModel.polarError

    return buildModel
