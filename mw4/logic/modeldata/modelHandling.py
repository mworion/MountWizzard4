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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
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
        mPoint['errorAngle'] = mountModel.starList[i].errorAngle.degrees
        mPoint['haMountModel'] = mountModel.starList[i].coord.ra.hours
        mPoint['decMountModel'] = mountModel.starList[i].coord.dec.degrees
        mPoint['errorRA'] = mountModel.starList[i].errorRA()
        mPoint['errorDEC'] = mountModel.starList[i].errorDEC()
        mPoint['errorIndex'] = mountModel.starList[i].number
        mPoint['modelTerms'] = mountModel.terms
        mPoint['modelErrorRMS'] = mountModel.errorRMS
        mPoint['modelOrthoError'] = mountModel.orthoError.degrees * 3600
        mPoint['modelPolarError'] = mountModel.polarError.degrees * 3600

    return buildModel
