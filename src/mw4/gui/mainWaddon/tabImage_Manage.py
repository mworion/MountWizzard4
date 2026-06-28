############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from mw4.gui.mainWaddon.tabAddon import TabAddon
from mw4.gui.utilities.nativeQt.qtInputDialog import MWInputDialog
from mw4.gui.utilities.qtHelpers import changeStyleDynamic, clickable, guiSetText
from typing import Any


class ImageManage(TabAddon):
    def __init__(self, mainW: Any) -> None:
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
        self.ui.lightPanelOn.clicked.connect(self.switchLightPanelOn)
        self.ui.lightPanelOff.clicked.connect(self.switchLightPanelOff)
        clickable(self.ui.lightPanelIntensity).connect(self.setLightPanelIntensity)

        self.ui.aperture.valueChanged.connect(self.updateImagingParam)
        self.ui.focalLength.valueChanged.connect(self.updateImagingParam)
        self.ui.exposureTime1.valueChanged.connect(self.updateImagingParam)
        self.ui.binning1.valueChanged.connect(self.updateImagingParam)
        self.ui.exposureTimeN.valueChanged.connect(self.updateImagingParam)
        self.ui.binningN.valueChanged.connect(self.updateImagingParam)
        self.ui.subFrame.valueChanged.connect(self.updateImagingParam)
        self.app.timeMgr.update1s.connect(self.updateImagingParam)

        self.ui.haltFocuser.clicked.connect(self.haltFocuser)
        self.ui.moveFocuserIn.clicked.connect(self.moveFocuserIn)
        self.ui.moveFocuserOut.clicked.connect(self.moveFocuserOut)
        self.app.dReg["hidController"].signals.hidSL.connect(self.domeMoveHid)

        self.app.timeMgr.update1s.connect(self.updateCoverStatGui)
        self.app.timeMgr.update1s.connect(self.updateLightPanelGui)
        self.app.timeMgr.update1s.connect(self.updateDomeGui)
        self.app.timeMgr.update1s.connect(self.updateShutterStatGui)

    def initConfig(self) -> None:
        config = self.app.config["WindowMain"]
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
        config = self.app.config["WindowMain"]
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
        self.mainW.wIcon(self.ui.copyFromTelescopeDriver, "copy")
        self.mainW.wIcon(self.ui.haltFocuser, "bolt-alt")
        self.mainW.wIcon(self.ui.moveFocuserIn, "exit-down")
        self.mainW.wIcon(self.ui.moveFocuserOut, "exit-up")
        self.mainW.wIcon(self.ui.coverPark, "exit-down")
        self.mainW.wIcon(self.ui.coverUnpark, "exit-up")

    def checkEnableCameraUI(self) -> None:
        coolerTemp = "CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE" in self.app.dReg["camera"].data
        gainCam = "CCD_GAIN.GAIN" in self.app.dReg["camera"].data
        offsetCam = "CCD_OFFSET.OFFSET" in self.app.dReg["camera"].data
        pixelX = "CCD_INFO.CCD_MAX_X" in self.app.dReg["camera"].data
        self.ui.GroupCooler.setEnabled(coolerTemp)
        self.ui.GroupGain.setEnabled(gainCam)
        self.ui.GroupOffset.setEnabled(offsetCam)
        self.ui.GroupControlledCamera.setEnabled(pixelX)

    def updateOffset(self) -> None:
        actValue = self.app.dReg["camera"].data.get("CCD_OFFSET.OFFSET", False)
        offsetList = self.app.dReg["camera"].data.get("CCD_OFFSET.OFFSET_LIST", False)
        if offsetList and actValue:
            offsetList = list(offsetList)
            self.mainW.log.debug(f"Index: [{actValue}], List: [{offsetList}]")
            if actValue > len(offsetList):
                actValue = len(offsetList)
            elif actValue < 0:
                actValue = 0
            guiSetText(self.ui.offsetCam, "s", offsetList[actValue - 1])
        else:
            guiSetText(self.ui.offsetCam, "3.0f", actValue)

    def updateGain(self) -> None:
        actValue = self.app.dReg["camera"].data.get("CCD_GAIN.GAIN", False)
        gainList = self.app.dReg["camera"].data.get("CCD_GAIN.GAIN_LIST", False)
        if gainList and actValue:
            gainList = list(gainList)
            self.mainW.log.debug(f"Index: [{actValue}], List: [{gainList}]")
            if actValue > len(gainList):
                actValue = len(gainList)
            elif actValue < 0:
                actValue = 0
            guiSetText(self.ui.gainCam, "s", gainList[actValue - 1])
        else:
            guiSetText(self.ui.gainCam, "3.0f", actValue)

    def updateCooler(self) -> None:
        coolerTemp = self.app.dReg["camera"].data.get(
            "CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE", 0
        )
        coolerPower = self.app.dReg["camera"].data.get("CCD_COOLER_POWER.CCD_COOLER_VALUE", 0)
        coolerOn = self.app.dReg["camera"].data.get("CCD_COOLER.COOLER_ON", False)
        guiSetText(self.ui.coolerTemp, "3.1f", coolerTemp)
        guiSetText(self.ui.coolerPower, "3.1f", coolerPower)
        if coolerOn:
            changeStyleDynamic(self.ui.coolerOn, "run", True)
            changeStyleDynamic(self.ui.coolerOff, "run", False)
        else:
            changeStyleDynamic(self.ui.coolerOn, "run", False)
            changeStyleDynamic(self.ui.coolerOff, "run", True)

    def updateFilter(self) -> None:
        filterNumber = self.app.dReg["filter"].data.get("FILTER_SLOT.FILTER_SLOT_VALUE", 1)
        key = f"FILTER_NAME.FILTER_SLOT_NAME_{filterNumber:1.0f}"
        filterName = self.app.dReg["filter"].data.get(key, "not found")
        guiSetText(self.ui.filterNumber, "1.0f", filterNumber)
        guiSetText(self.ui.filterName, "s", filterName)

    def updateFocuser(self) -> None:
        focus = self.app.dReg["focuser"].data.get(
            "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION", 0
        )
        guiSetText(self.ui.focuserPosition, "6.0f", focus)

    def updateImagingParam(self) -> None:
        self.checkEnableCameraUI()
        self.updateOffset()
        self.updateGain()
        self.updateCooler()
        self.updateFilter()
        self.updateFocuser()
        camera = self.app.dReg["camera"].instance

        focalLength = self.ui.focalLength.value()
        maxBinX = camera.data.get("CCD_BINNING.HOR_BIN_MAX", 9)
        maxBinY = camera.data.get("CCD_BINNING.HOR_BIN_MAX", 9)
        pixelX = camera.data.get("CCD_INFO.CCD_MAX_X", 0)
        pixelY = camera.data.get("CCD_INFO.CCD_MAX_Y", 0)

        optimalBinningX = int(pixelX / 1750)
        optimalBinningY = int(pixelY / 1750)
        optimalBinning = max(1, min(optimalBinningX, optimalBinningY))

        if maxBinX and maxBinY:
            maxBin = min(maxBinX, maxBinY)
            self.ui.binning1.setMaximum(maxBin)
            self.ui.binningN.setMaximum(maxBin)

        camera.exposureTime1 = self.ui.exposureTime1.value()
        camera.exposureTimeN = self.ui.exposureTimeN.value()
        camera.binning1 = self.ui.binning1.value()
        camera.binningN = self.ui.binningN.value()
        camera.subFrame = self.ui.subFrame.value()
        camera.fastDownload = True
        camera.focalLength = focalLength
        guiSetText(self.ui.optimalBinning, "1.0f", optimalBinning)

    def setCoolerTemp(self) -> None:
        canSetCCDTemp = self.app.dReg["camera"].data.get("CAN_SET_CCD_TEMPERATURE", False)
        if not canSetCCDTemp:
            return

        actValue = self.app.dReg["camera"].data.get(
            "CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE", None
        )
        if actValue is None:
            return

        actValue = int(actValue)
        value, ok = MWInputDialog.getInt(
            self.mainW, "Set cooler temperature", "Value (-30..+20):", actValue, -30, 20, 1
        )
        if ok:
            self.app.dReg["camera"].instance.sendCoolerTemp(temperature=value)

    def setOffset(self) -> None:
        actValue = self.app.dReg["camera"].data.get("CCD_OFFSET.OFFSET", None)
        if actValue is None:
            return

        actValue = int(actValue)
        offsetList = self.app.dReg["camera"].data.get("CCD_OFFSET.OFFSET_LIST")
        offsetMin = self.app.dReg["camera"].data.get("CCD_OFFSET.OFFSET_MIN")
        offsetMax = self.app.dReg["camera"].data.get("CCD_OFFSET.OFFSET_MAX")
        if offsetList is not None:
            offsetList = list(offsetList)
            value, ok = MWInputDialog.getItem(
                self.mainW, "Set offset", "Offset entry: ", offsetList, actValue
            )
            value = offsetList.index(value)

        elif offsetMin is not None and offsetMax is not None:
            offsetMin = int(offsetMin)
            offsetMax = int(offsetMax)
            value, ok = MWInputDialog.getInt(
                self.mainW,
                "Set offset",
                f"Values ({offsetMin:4}..{offsetMax:4}):",
                actValue,
                offsetMin,
                offsetMax,
                int((offsetMax - offsetMin) / 20),
            )
        else:
            value, ok = MWInputDialog.getInt(self.mainW, "Set offset", "Values:", actValue)
        if ok:
            self.app.dReg["camera"].instance.sendOffset(offset=value)

    def setGain(self) -> None:
        actValue = self.app.dReg["camera"].data.get("CCD_GAIN.GAIN", None)
        if actValue is None:
            return
        actValue = int(actValue)
        gainList = self.app.dReg["camera"].data.get("CCD_GAIN.GAIN_LIST")
        gainMin = self.app.dReg["camera"].data.get("CCD_GAIN.GAIN_MIN")
        gainMax = self.app.dReg["camera"].data.get("CCD_GAIN.GAIN_MAX")
        if gainList is not None:
            gainList = list(gainList)
            value, ok = MWInputDialog.getItem(
                self.mainW, "Set gain", "Gain entry: ", gainList, actValue
            )
            value = gainList.index(value)

        elif gainMin is not None and gainMax is not None:
            gainMin = int(gainMin)
            gainMax = int(gainMax)
            value, ok = MWInputDialog.getInt(
                self.mainW,
                "Set gain",
                f"Values ({gainMin:4}..{gainMax:4}):",
                actValue,
                gainMin,
                gainMax,
                int((gainMax - gainMin) / 20),
            )
        else:
            value, ok = MWInputDialog.getInt(self.mainW, "Set gain", "Values:", actValue)

        if ok:
            self.app.dReg["camera"].instance.sendGain(gain=value)

    def setFilterNumber(self) -> None:
        data = self.app.dReg["filter"].data
        actValue = data.get("FILTER_SLOT.FILTER_SLOT_VALUE")
        if actValue is None:
            return
        actValue = int(actValue)

        availNames = [data[key] for key in data if "FILTER_NAME.FILTER_SLOT_NAME_" in key]
        numberFilter = len(availNames)
        isAlpaca = "FILTER_NAME.FILTER_SLOT_NAME_0" in data
        if isAlpaca:
            start = 0
            end = numberFilter - 1
        else:
            start = 1
            end = numberFilter

        value, ok = MWInputDialog.getInt(
            self.mainW,
            "Set filter number",
            f"Value ({start}..{end}):",
            actValue,
            start,
            end,
            1,
        )
        if ok:
            self.app.dReg["filter"].instance.sendFilterNumber(filterNumber=value)

    def setFilterName(self) -> None:
        data = self.app.dReg["filter"].data
        actValue = data.get("FILTER_SLOT.FILTER_SLOT_VALUE")
        if actValue is None:
            return
        actValue = int(actValue)

        availNames = [data[key] for key in data if "FILTER_NAME.FILTER_SLOT_NAME_" in key]

        value, ok = MWInputDialog.getItem(
            self.mainW, "Set filter", "Filter Name: ", availNames, actValue - 1
        )
        self.mainW.log.debug(f"FilterSelected: [{value}], FilterList: [{availNames}]")
        if not ok:
            return
        isAlpaca = "FILTER_NAME.FILTER_SLOT_NAME_0" in data
        number = availNames.index(value) if isAlpaca else availNames.index(value) + 1
        self.app.dReg["filter"].instance.sendFilterNumber(filterNumber=number)

    def setCoolerOn(self) -> None:
        self.app.dReg["camera"].instance.sendCoolerSwitch(coolerOn=True)

    def setCoolerOff(self) -> None:
        self.app.dReg["camera"].instance.sendCoolerSwitch(coolerOn=False)

    def updateCoverStatGui(self) -> None:
        value = self.app.dReg["cover"].data.get("CAP_PARK.PARK", None)
        if value:
            changeStyleDynamic(self.ui.coverPark, "run", True)
            changeStyleDynamic(self.ui.coverUnpark, "run", False)
        elif value is None:
            changeStyleDynamic(self.ui.coverPark, "run", False)
            changeStyleDynamic(self.ui.coverUnpark, "run", False)
        else:
            changeStyleDynamic(self.ui.coverPark, "run", False)
            changeStyleDynamic(self.ui.coverUnpark, "run", True)

        value = self.app.dReg["cover"].data.get("Status.Cover", "-")
        self.ui.coverStatusText.setText(value)

    def updateLightPanelGui(self) -> None:
        value = self.app.dReg["lightPanel"].data.get("FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON", None)
        if value:
            changeStyleDynamic(self.ui.lightPanelOn, "run", True)
            changeStyleDynamic(self.ui.lightPanelOff, "run", False)
        elif value is None:
            changeStyleDynamic(self.ui.lightPanelOn, "run", False)
            changeStyleDynamic(self.ui.lightPanelOff, "run", False)
        else:
            changeStyleDynamic(self.ui.lightPanelOn, "run", False)
            changeStyleDynamic(self.ui.lightPanelOff, "run", True)

        value = self.app.dReg["lightPanel"].data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE"
        )
        guiSetText(self.ui.lightPanelIntensity, "3.0f", value)

    def setCoverPark(self) -> None:
        self.app.dReg["cover"].instance.closeCover()

    def setCoverUnpark(self) -> None:
        self.app.dReg["cover"].instance.openCover()

    def setCoverHalt(self) -> None:
        self.app.dReg["cover"].instance.haltCover()

    def moveFocuserIn(self) -> None:
        pos = self.app.dReg["focuser"].data.get(
            "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION", 0
        )
        step = self.ui.focuserSteps.value()
        newPos = int(pos - step)
        self.app.dReg["focuser"].instance.move(position=newPos)

    def moveFocuserOut(self) -> None:
        pos = self.app.dReg["focuser"].data.get(
            "ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION", 0
        )
        step = self.ui.focuserSteps.value()
        newPos = int(pos + step)
        self.app.dReg["focuser"].instance.move(position=newPos)

    def haltFocuser(self) -> None:
        self.app.dReg["focuser"].instance.halt()

    def switchLightPanelOn(self) -> None:
        self.app.dReg["lightPanel"].instance.lightOn()

    def switchLightPanelOff(self) -> None:
        self.app.dReg["lightPanel"].instance.lightOff()

    def setLightPanelIntensity(self) -> None:
        actValue = self.app.dReg["lightPanel"].data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE", 0
        )
        maxBrightness = self.app.dReg["lightPanel"].data.get(
            "FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_MAX", 255
        )
        value, ok = MWInputDialog.getInt(
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
        self.ui.lightPanelIntensity.setText(f"{value}")
        self.app.dReg["lightPanel"].instance.lightIntensity(int(value))

    def updateDomeGui(self) -> None:
        value = self.app.dReg["dome"].data.get("DOME_MOTION.DOME_CW", None)
        if value:
            changeStyleDynamic(self.ui.domeSlewCW, "run", True)
        else:
            changeStyleDynamic(self.ui.domeSlewCW, "run", False)

        value = self.app.dReg["dome"].data.get("DOME_MOTION.DOME_CCW", None)
        if value:
            changeStyleDynamic(self.ui.domeSlewCCW, "run", True)
        else:
            changeStyleDynamic(self.ui.domeSlewCCW, "run", False)

        value = self.app.dReg["dome"].data.get("ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION")
        guiSetText(self.ui.domeAzimuth, "3.0f", value)

    def updateShutterStatGui(self) -> None:
        value = self.app.dReg["dome"].instance.data.get("DOME_SHUTTER.SHUTTER_OPEN", None)
        if value is True:
            changeStyleDynamic(self.ui.domeOpenShutter, "run", True)
            changeStyleDynamic(self.ui.domeCloseShutter, "run", False)
        elif value is False:
            changeStyleDynamic(self.ui.domeOpenShutter, "run", False)
            changeStyleDynamic(self.ui.domeCloseShutter, "run", True)
        else:
            changeStyleDynamic(self.ui.domeOpenShutter, "run", False)
            changeStyleDynamic(self.ui.domeCloseShutter, "run", False)

        value = self.app.dReg["dome"].instance.data.get("Status.Shutter", None)
        if value:
            self.ui.domeShutterStatusText.setText(value)

    def domeSlewCW(self) -> None:
        if not self.app.dReg["dome"].stat:
            return
        self.app.dReg["dome"].instance.slewCW()

    def domeSlewCCW(self) -> None:
        if not self.app.dReg["dome"].stat:
            return
        self.app.dReg["dome"].instance.slewCCW()

    def domeAbortSlew(self) -> None:
        if not self.app.dReg["dome"].stat:
            return
        self.app.dReg["dome"].instance.abortSlew()

    def domeOpenShutter(self) -> None:
        if not self.app.dReg["dome"].stat:
            return
        self.app.dReg["dome"].instance.openShutter()

    def domeCloseShutter(self) -> None:
        if not self.app.dReg["dome"].stat:
            return
        self.app.dReg["dome"].instance.closeShutter()

    def domeMoveHid(self, turnVal: int, openVal: int) -> None:
        if not self.app.dReg["dome"].stat:
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
