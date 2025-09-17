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

# external packages

# local import


class Device:
    """
    Device implements an INDI Device. it relies on PySide6 and it's signalling
    scheme. there might be not all capabilities implemented right now. all the
    data, properties and attributes are stored in a device dict.
    """

    __all__ = ["Device"]

    log = logging.getLogger("MW4")

    def __init__(self, name=""):
        super().__init__()

        self.name = name
        self.connected = False

    def getNumber(self, propertyName):
        """
        getNumber extracts from the device dictionary the relevant property
        subset for number or list of number elements. the return dict could be
        used later on for setting an element list (number vector) in indi client.

        :param propertyName: string with name
        :return: dict with number / number vector
        """
        if not hasattr(self, propertyName):
            return {}

        iProperty = getattr(self, propertyName)
        if iProperty["propertyType"] not in ["defNumberVector", "setNumberVector"]:
            self.log.warning(f"Property: {iProperty['propertyType']} is not Number")
            return {}

        elementList = iProperty["elementList"]
        retDict = {}
        for prop in elementList:
            retDict[prop] = elementList[prop]["value"]

        return retDict

    def getText(self, propertyName):
        """
        getNumber extracts from the device dictionary the relevant property
        subset for text or list of text elements. the return dict could be used
        later on for setting an element list (text vector) in indi client.

        :param propertyName: string with name
        :return: dict with text or text vector
        """
        if not hasattr(self, propertyName):
            return {}

        iProperty = getattr(self, propertyName)
        if iProperty["propertyType"] not in ["defTextVector", "setTextVector"]:
            self.log.warning(f"Property: {iProperty['propertyType']} is not Text")
            return {}

        elementList = iProperty["elementList"]
        retDict = {}
        for prop in elementList:
            retDict[prop] = elementList[prop]["value"]

        return retDict

    def getSwitch(self, propertyName):
        """
        getSwitch extracts from the device dictionary the relevant property
        subset for switch or list of switch elements. the return dict could be
        used later on for setting an element list (switch vector) in indi client.

        :param propertyName: string with name
        :return: dict with switch or switch vector
        """
        if not hasattr(self, propertyName):
            return {}

        iProperty = getattr(self, propertyName)
        if iProperty["propertyType"] not in ["defSwitchVector", "setSwitchVector"]:
            self.log.warning(f"Property: {iProperty['propertyType']} is not Switch")
            return {}

        elementList = iProperty["elementList"]
        retDict = {}
        for prop in elementList:
            retDict[prop] = elementList[prop]["value"]

        return retDict

    def getLight(self, propertyName):
        """
        getLight extracts from the device dictionary the relevant property
        subset for light or list of light elements. the return dict could be used
        later on for setting an element list (light vector) in indi client.

        :param propertyName: string with name
        :return: dict with light or light vector
        """
        if not hasattr(self, propertyName):
            return {}

        iProperty = getattr(self, propertyName)
        if iProperty["propertyType"] not in ["defLightVector", "setLightVector"]:
            self.log.warning(f"Property: {iProperty['propertyType']} is not Light")
            return {}

        elementList = iProperty["elementList"]
        retDict = {}
        for prop in elementList:
            retDict[prop] = elementList[prop]["value"]

        return retDict

    def getBlob(self, propertyName):
        """
        getBlob extracts from the device dictionary the relevant property
        value for blob.

        :param propertyName: string with name
        :return: return blob
        """
        if not hasattr(self, propertyName):
            return {}

        iProperty = getattr(self, propertyName)
        if iProperty["propertyType"] not in ["defBLOBVector", "setBLOBVector"]:
            self.log.warning(f"Property: {iProperty['propertyType']} is not Blob")
            return {}

        return iProperty["elementList"][propertyName]
