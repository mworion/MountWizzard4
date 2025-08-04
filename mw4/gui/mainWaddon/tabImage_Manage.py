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

# external packages
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import QObject

# local import
from gui.utilities.toolsQtWidget import changeStyleDynamic, guiSetText, clickable


class ImageManage(QObject):
    """ """

    def __init__(self, mainW):
        super().__init__()
        self.mainW = mainW
        self.app = mainW.app
        self.msg = mainW.app.msg
        self.ui = mainW.ui

        self.ui.coolerOn.clicked.connect(self.setCoolerOn)
        self.ui.coolerOff.clicked.connect(self.setCoolerOff)
        clickable(self.ui.coolerTemp).connect(self.setCoolerTemp)
        clickable(self.ui.gainCam).connect(self.setGain)
        clickable(self.ui.offsetCam).connect(self.setOffset)
        clickable(self.ui.filterNumber).connect(self.setFilterNumber)
        clickable(self.ui.filterName).connect(self.setFilterName)
        self.ui.coverPark.clicked.connect(self.setCoverPark)
        self.ui.coverUnpark.clicked.connect(self.setCoverUnpark)
        self.ui.domeSlewCW.clicked.connect(self.domeSlewCW)
        self.ui.domeSlewCCW.clicked.connect(self.domeSlewCCW)
        self.ui.domeAbortSlew.clicked.connect(self.domeAbortSlew)
        self.ui.domeOpenShutter.clicked.connect(self.domeOpenShutter)
        self.ui.domeCloseShutter.clicked.connect(self.domeCloseShutter)
        self.ui.coverHalt.clicked.connect(self.setCoverHalt)
        self.ui.coverLightOn.clicked.connect(self.switchLightOn)
        self.ui.coverLightOff.clicked.connect(self.switchLightOff)
        clickable(self.ui.coverLightIntensity).connect(self.setLightIntensity)

        self.ui.aperture.valueChanged.connect(self.updateImagingParam)
        self.ui.focalLength.valueChanged.connect(self.updateImagingParam)
        self.ui.exposureTime1.valueChanged.connect(self.updateImagingParam)
        self.ui.binning1.valueChanged.connect(self.updateImagingParam)
        self.ui.exposureTimeN.valueChanged.connect(self.updateImagingParam)
        self.ui.binningN.valueChanged.connect(self.updateImagingParam)
        self.ui.subFrame.valueChanged.connect(self.updateImagingParam)
        self.app.update1s.connect(self.updateImagingParam)

        self.ui.haltFocuser.clicked.connect(self.haltFocuser)
        self.ui.moveFocuserIn.clicked.connect(self.moveFocuserIn)
        self.ui.moveFocuserOut.clicked.connect(self.moveFocuserOut)
        self.app.game_sL.connect(self.domeMoveGameController)

        self.app.update1s.connect(self.updateCoverStatGui)
        self.app.update1s.connect(self.updateCoverLightGui)
        self.app.update1s.connect(self.updateDomeGui)
        self.app.update1s.connect(self.updateShutterStatGui)

    def initConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        self.ui.exposureTime1.setValue(config.get("exposureTime1", 1))
        self.ui.binning1.setValue(config.get("binning1", 1))
        self.ui.exposureTimeN.setValue(config.get("exposureTimeN", 1))
        self.ui.binningN.setValue(config.get("binningN", 1))
        self.ui.subFrame.setValue(config.get("subFrame", 100))
        self.ui.focalLength.setValue(config.get("focalLength", 100))
        self.ui.aperture.setValue(config.get("aperture", 100))
        self.ui.focuserStepsize.setValue(config.get("focuserStepsize", 100))
        self.ui.focuserSteps.setValue(config.get("focuserSteps", 100))

    def storeConfig(self) -> None:
        """ """
        config = self.app.config["mainW"]
        config["exposureTime1"] = self.ui.exposureTime1.value()
        config["binning1"] = self.ui.binning1.value()
        config["exposureTimeN"] = self.ui.exposureTimeN.value()
        config["binningN"] = self.ui.binningN.value()
        config["subFrame"] = self.ui.subFrame.value()
        config["focalLength"] = self.ui.focalLength.value()
        config["aperture"] = self.ui.aperture.value()
        config["focuserStepsize"] = self.ui.focuserStepsize.value()
        config["focuserSteps"] = self.ui.focuserSteps.value()

    def setupIcons(self) -> None:
        """ """
        self.mainW.wIcon(self.ui.copyFromTelescopeDriver, "copy")
        self.mainW.wIcon(self.ui.haltFocuser, "bolt-alt")
        self.mainW.wIcon(self.ui.moveFocuserIn, "exit-down")
        self.mainW.wIcon(self.ui.moveFocuserOut, "exit-up")
        self.mainW.wIcon(self.ui.coverPark, "exit-down")
        self.mainW.wIcon(self.ui.coverUnpark, "exit-up")

    def checkEnableCameraUI(self) -> None:
        """ """
        coolerTemp = self.app.camera.data.get("CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE")
        coolerPower = self.app.camera.data.get("CCD_COOLER_POWER.CCD_COOLER_VALUE")
        gainCam = self.app.camera.data.get("CCD_GAIN.GAIN")
        offsetCam = self.app.camera.data.get("CCD_OFFSET.OFFSET")
        humidityCCD = self.app.camera.data.get("CCD_HUMIDITY.HUMIDITY")
        coolerOn = self.app.camera.data.get("CCD_COOLER.COOLER_ON")
        pixelX = self.app.camera.data.get("CCD_INFO.CCD_MAX_X")

        enable = coolerTemp is not None
        self.ui.coolerTemp.setVisible(enable)
        enable = coolerPower is not None
        self.ui.coolerPower.setVisible(enable)
        enable = gainCam is not None
        self.ui.gainCam.setVisible(enable)
        enable = offsetCam is not None
        self.ui.offsetCam.setVisible(enable)
        enable = humidityCCD is not None
        self.ui.humidityCCD.setVisible(enable)
        enable = coolerOn is not None
        self.ui.coolerOn.setVisible(enable)
        self.ui.coolerOff.setVisible(enable)
        enable = pixelX is not None
        self.ui.subFrame.setVisible(enable)

    def updateOffset(self) -> None:
        """ """
        actValue = self.app.camera.data.get("CCD_OFFSET.OFFSET")
        offsetList = self.app.camera.data.get("CCD_OFFSET.OFFSET_LIST")
        if offsetList is not None and actValue is not None:
            offsetList = list(offsetList)
            self.mainW.log.debug(f"Index: [{actValue}], List: [{offsetList}]")
            if len(offsetList) == 0:
                offsetList = ["0"]
            if actValue > len(offsetList):
                actValue = len(offsetList)
            elif actValue < 0:
                actValue = 0
            guiSetText(self.ui.offsetCam, "s", offsetList[actValue - 1])
        else:
            guiSetText(self.ui.offsetCam, "3.0f", actValue)

    def updateGain(self) -> None:
        """ """
        actValue = self.app.camera.data.get("CCD_GAIN.GAIN")
        gainList = self.app.camera.data.get("CCD_GAIN.GAIN_LIST")
        if gainList is not None and actValue is not None:
            gainList = list(gainList)
            self.mainW.log.debug(f"Index: [{actValue}], List: [{gainList}]")
            if len(gainList) == 0:
                gainList = ["1"]
            if actValue > len(gainList):
                actValue = len(gainList)
            elif actValue < 0:
                actValue = 0
            guiSetText(self.ui.gainCam, "s", gainList[actValue - 1])
        else:
            guiSetText(self.ui.gainCam, "3.0f", actValue)

    def updateCooler(self) -> None:
        """ """
        coolerTemp = self.app.camera.data.get("CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE", 0)
        coolerPower = self.app.camera.data.get("CCD_COOLER_POWER.CCD_COOLER_VALUE", 0)
        coolerOn = self.app.camera.data.get("CCD_COOLER.COOLER_ON", False)
        guiSetText(self.ui.coolerTemp, "3.1f", coolerTemp)
        guiSetText(self.ui.coolerPower, "3.1f", coolerPower)
        if coolerOn:
            changeStyleDynamic(self.ui.coolerOn, "running", True)
            changeStyleDynamic(self.ui.coolerOff, "running", False)
        else:
            changeStyleDynamic(self.ui.coolerOn, "running", False)
            changeStyleDynamic(self.ui.coolerOff, "running", True)

    def updateFilter(self) -> None:
        """ """
        filterNumber = self.app.filter.data.get("FILTER_SLOT.FILTER_SLOT_VALUE", 1)
        key = f"FILTER_NAME.FILTER_SLOT_NAME_{filterNumber:1.0f}"
        filterName = self.app.filter.data.get(key, "not found")
        guiSetText(self.ui.filterNumber, "1.0f", filterNumber)
        guiSetText(self.ui.filterName, "s", filterName)

    def updateFocuser(self) -> None:
        """ """
        focus = self.app.focuser.data.get("ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION", 0)
        guiSetText(self.ui.focuserPosition, "6.0f", focus)

    def updateImagingParam(self) -> None:
        """ """
        self.checkEnableCameraUI()
        self.updateOffset()
        self.updateGain()
        self.updateCooler()
        self.updateFilter()
        self.updateFocuser()

        focalLength = self.ui.focalLength.value()
        maxBinX = self.app.camera.data.get("CCD_BINNING.HOR_BIN_MAX", 9)
        maxBinY = self.app.camera.data.get("CCD_BINNING.HOR_BIN_MAX", 9)
        pixelX = self.app.camera.data.get("CCD_INFO.CCD_MAX_X", 0)
        pixelY = self.app.camera.data.get("CCD_INFO.CCD_MAX_Y", 0)
        humidityCCD = self.app.camera.data.get("CCD_HUMIDITY.HUMIDITY")

        optimalBinningX = int(pixelX / 1750)
        optimalBinningY = int(pixelY / 1750)
        optimalBinning = max(1, min(optimalBinningX, optimalBinningY))

        if maxBinX and maxBinY:
            maxBin = min(maxBinX, maxBinY)
            self.ui.binning1.setMaximum(maxBin)
            self.ui.binningN.setMaximum(maxBin)

        self.app.camera.exposureTime1 = self.ui.exposureTime1.value()
        self.app.camera.exposureTimeN = self.ui.exposureTimeN.value()
        self.app.camera.binning1 = self.ui.binning1.value()
        self.app.camera.binningN = self.ui.binningN.value()
        self.app.camera.subFrame = self.ui.subFrame.value()
        self.app.camera.fastDownload = True
        self.app.camera.focalLength = focalLength
        guiSetText(self.ui.humidityCCD, "3.1f", humidityCCD)
        guiSetText(self.ui.optimalBinning, "1.0f", optimalBinning)

    def setCoolerTemp(self) -> None:
        """ """
        canSetCCDTemp = self.app.camera.data.get("CAN_SET_CCD_TEMPERATURE", False)
        if not canSetCCDTemp:
            return

        actValue = self.app.camera.data.get("CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE", None)
        if actValue is None:
            return

        actValue = int(actValue)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self, "Set cooler temperature", "Value (-30..+20):", actValue, -30, 20, 1
        )
        if ok:
            self.app.camera.sendCoolerTemp(temperature=value)

    def setOffset(self) -> None:
        """ """
        actValue = self.app.camera.data.get("CCD_OFFSET.OFFSET", None)
        if actValue is None:
            return

        actValue = int(actValue)
        dlg = QInputDialog()
        offsetList = self.app.camera.data.get("CCD_OFFSET.OFFSET_LIST")
        offsetMin = self.app.camera.data.get("CCD_OFFSET.OFFSET_MIN")
        offsetMax = self.app.camera.data.get("CCD_OFFSET.OFFSET_MAX")
        if offsetList is not None:
            offsetList = list(offsetList)
            value, ok = dlg.getItem(self, "Set offset", "Offset entry: ", offsetList, actValue)
            value = offsetList.index(value)

        elif offsetMin is not None and offsetMax is not None:
            offsetMin = int(offsetMin)
            offsetMax = int(offsetMax)
            value, ok = dlg.getInt(
                self,
                "Set offset",
                f"Values ({offsetMin:4}..{offsetMax:4}):",
                actValue,
                offsetMin,
                offsetMax,
                int((offsetMax - offsetMin) / 20),
            )
        else:
            value, ok = dlg.getInt(self, "Set offset", "Values:", actValue)
        if ok:
            self.app.camera.sendOffset(offset=value)

    def setGain(self) -> None:
        """ """
        actValue = self.app.camera.data.get("CCD_GAIN.GAIN", None)
        if actValue is None:
            return
        actValue = int(actValue)
        dlg = QInputDialog()
        gainList = self.app.camera.data.get("CCD_GAIN.GAIN_LIST")
        gainMin = self.app.camera.data.get("CCD_GAIN.GAIN_MIN")
        gainMax = self.app.camera.data.get("CCD_GAIN.GAIN_MAX")
        if gainList is not None:
            gainList = list(gainList)
            value, ok = dlg.getItem(self, "Set gain", "Gain entry: ", gainList, actValue)
            value = gainList.index(value)

        elif gainMin is not None and gainMax is not None:
            gainMin = int(gainMin)
            gainMax = int(gainMax)
            value, ok = dlg.getInt(
                self,
                "Set gain",
                f"Values ({gainMin:4}..{gainMax:4}):",
                actValue,
                gainMin,
                gainMax,
                int((gainMax - gainMin) / 20),
            )
        else:
            value, ok = dlg.getInt(self, "Set gain", "Values:", actValue)

        if ok:
            self.app.camera.sendGain(gain=value)

    def setFilterNumber(self) -> None:
        """ """
        data = self.app.filter.data
        actValue = data.get("FILTER_SLOT.FILTER_SLOT_VALUE")
        if actValue is None:
            return
        actValue = int(actValue)

        availNames = list(data[key] for key in data if "FILTER_NAME.FILTER_SLOT_NAME_" in key)
        numberFilter = len(availNames)
        isAlpaca = "FILTER_NAME.FILTER_SLOT_NAME_0" in data
        if isAlpaca:
            start = 0
            end = numberFilter - 1
        else:
            start = 1
            end = numberFilter

        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self,
            "Set filter number",
            f"Value ({start}..{end}):",
            actValue,
            start,
            end,
            1,
        )
        if ok:
            self.app.filter.sendFilterNumber(filterNumber=value)

    def setFilterName(self) -> None:
        """ """
        data = self.app.filter.data
        actValue = data.get("FILTER_SLOT.FILTER_SLOT_VALUE")
        if actValue is None:
            return
        actValue = int(actValue)

        availNames = list(data[key] for key in data if "FILTER_NAME.FILTER_SLOT_NAME_" in key)

        dlg = QInputDialog()
        value, ok = dlg.getItem(self, "Set filter", "Filter Name: ", availNames, actValue - 1)
        self.mainW.log.debug(f"FilterSelected: [{value}], FilterList: [{availNames}]")
        if not ok:
            return
        isAlpaca = "FILTER_NAME.FILTER_SLOT_NAME_0" in data
        if isAlpaca:
            number = availNames.index(value)
        else:
            number = availNames.index(value) + 1
        self.app.filter.sendFilterNumber(filterNumber=number)

    def setCoolerOn(self) -> None:
        """ """
        self.app.camera.sendCoolerSwitch(coolerOn=True)

    def setCoolerOff(self) -> None:
        """ """
        self.app.camera.sendCoolerSwitch(coolerOn=False)

    def updateCoverStatGui(self) -> None:
        """ """
        value = self.app.cover.data.get("CAP_PARK.PARK", None)
        if value:
            changeStyleDynamic(self.ui.coverPark, "running", True)
            changeStyleDynamic(self.ui.coverUnpark, "running", False)
        elif value is None:
            changeStyleDynamic(self.ui.coverPark, "running", False)
            changeStyleDynamic(self.ui.coverUnpark, "running", False)
        else:
            changeStyleDynamic(self.ui.coverPark, "running", False)
            changeStyleDynamic(self.ui.coverUnpark, "running", True)

        value = self.app.cover.data.get("Status.Cover", "-")
        self.ui.coverStatusText.setText(value)

    def updateCoverLightGui(self) -> None:
        """ """
        value = self.app.cover.data.get("FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON", None)
        if value:
            changeStyleDynamic(self.ui.coverLightOn, "running", True)
            changeStyleDynamic(self.ui.coverLightOff, "running", False)
        elif value is None:
            changeStyleDynamic(self.ui.coverLightOn, "running", False)
            changeStyleDynamic(self.ui.coverLightOff, "running", False)
        else:
            changeStyleDynamic(self.ui.coverLightOn, "running", False)
            changeStyleDynamic(self.ui.coverLightOff, "running", True)

        value = self.app.cover.data.get("FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE")
        guiSetText(self.ui.coverLightIntensity, "3.0f", value)

    def setCoverPark(self) -> None:
        """ """
        self.app.cover.closeCover()

    def setCoverUnpark(self) -> None:
        """ """
        self.app.cover.openCover()

    def setCoverHalt(self) -> None:
        """ """
        self.app.cover.haltCover()

    def moveFocuserIn(self) -> None:
        """ """
        pos = self.app.focuser.data.get("ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION", 0)
        step = self.ui.focuserSteps.value()
        newPos = pos - step
        self.app.focuser.move(position=newPos)

    def moveFocuserOut(self) -> None:
        """ """
        pos = self.app.focuser.data.get("ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION", 0)
        step = self.ui.focuserSteps.value()
        newPos = pos + step
        self.app.focuser.move(position=newPos)

    def haltFocuser(self) -> None:
        """ """
        self.app.focuser.halt()

    def switchLightOn(self) -> None:
        """ """
        self.app.cover.lightOn()

    def switchLightOff(self) -> None:
        """ """
        self.app.cover.lightOff()

    def setLightIntensity(self) -> None:
        """ """
        actValue = self.app.cover.data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE", 0
        )
        maxBrightness = self.app.cover.data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX", 255
        )

        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self.mainW,
            "Set intensity",
            f"Value (0..{maxBrightness}):",
            actValue,
            0,
            maxBrightness,
            1,
        )
        if not ok:
            return

        self.ui.coverLightIntensity.setText(f"{value}")
        self.app.cover.lightIntensity(value)

    def updateDomeGui(self) -> None:
        """ """
        value = self.app.dome.data.get("DOME_MOTION.DOME_CW", None)
        if value:
            changeStyleDynamic(self.ui.domeSlewCW, "running", True)
        else:
            changeStyleDynamic(self.ui.domeSlewCW, "running", False)

        value = self.app.dome.data.get("DOME_MOTION.DOME_CCW", None)
        if value:
            changeStyleDynamic(self.ui.domeSlewCCW, "running", True)
        else:
            changeStyleDynamic(self.ui.domeSlewCCW, "running", False)

        value = self.app.dome.data.get("ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION")
        guiSetText(self.ui.domeAzimuth, "3.0f", value)

    def updateShutterStatGui(self) -> None:
        """ """
        value = self.app.dome.data.get("DOME_SHUTTER.SHUTTER_OPEN", None)
        if value is True:
            changeStyleDynamic(self.ui.domeOpenShutter, "running", True)
            changeStyleDynamic(self.ui.domeCloseShutter, "running", False)
        elif value is False:
            changeStyleDynamic(self.ui.domeOpenShutter, "running", False)
            changeStyleDynamic(self.ui.domeCloseShutter, "running", True)
        else:
            changeStyleDynamic(self.ui.domeOpenShutter, "running", False)
            changeStyleDynamic(self.ui.domeCloseShutter, "running", False)

        value = self.app.dome.data.get("Status.Shutter", None)
        if value:
            self.ui.domeShutterStatusText.setText(value)

    def domeSlewCW(self) -> None:
        """ """
        if not self.app.deviceStat["dome"]:
            return
        self.app.dome.slewCW()

    def domeSlewCCW(self) -> None:
        """ """
        if not self.app.deviceStat["dome"]:
            return
        self.app.dome.slewCCW()

    def domeAbortSlew(self) -> None:
        """ """
        if not self.app.deviceStat["dome"]:
            return
        self.app.dome.abortSlew()

    def domeOpenShutter(self) -> None:
        """ """
        if not self.app.deviceStat["dome"]:
            return
        self.app.dome.openShutter()

    def domeCloseShutter(self) -> None:
        """ """
        if not self.app.deviceStat["dome"]:
            return
        self.app.dome.closeShutter()

    def domeMoveGameController(self, turnVal: int, openVal: int) -> None:
        """ """
        if not self.app.deviceStat["dome"]:
            return

        if turnVal < 64:
            self.domeSlewCCW()
        elif turnVal > 192:
            self.domeSlewCW()
        else:
            self.domeAbortSlew()

        if openVal < 64:
            self.domeOpenShutter()
        elif openVal > 192:
            self.domeCloseShutter()
