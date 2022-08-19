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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtWidgets import QInputDialog

# local import


class SettImaging:
    """
    """

    def __init__(self):
        self.ui.downloadFast.clicked.connect(self.setDownloadModeFast)
        self.ui.downloadSlow.clicked.connect(self.setDownloadModeSlow)
        self.ui.coolerOn.clicked.connect(self.setCoolerOn)
        self.ui.coolerOff.clicked.connect(self.setCoolerOff)
        self.clickable(self.ui.coolerTemp).connect(self.setCoolerTemp)
        self.clickable(self.ui.gainCam).connect(self.setGain)
        self.clickable(self.ui.offsetCam).connect(self.setOffset)
        self.clickable(self.ui.filterNumber).connect(self.setFilterNumber)
        self.clickable(self.ui.filterName).connect(self.setFilterName)
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
        self.clickable(self.ui.coverLightIntensity).connect(self.setLightIntensity)
        self.ui.aperture.valueChanged.connect(self.updateImagingParam)
        self.ui.focalLength.valueChanged.connect(self.updateImagingParam)
        self.ui.expTime.valueChanged.connect(self.updateImagingParam)
        self.ui.binning.valueChanged.connect(self.updateImagingParam)
        self.ui.expTimeN.valueChanged.connect(self.updateImagingParam)
        self.ui.binningN.valueChanged.connect(self.updateImagingParam)
        self.ui.subFrame.valueChanged.connect(self.updateImagingParam)
        self.ui.haltFocuser.clicked.connect(self.haltFocuser)
        self.ui.moveFocuserIn.clicked.connect(self.moveFocuserIn)
        self.ui.moveFocuserOut.clicked.connect(self.moveFocuserOut)
        self.app.game_sL.connect(self.domeMoveGameController)
        self.app.update1s.connect(self.updateCoverStatGui)
        self.app.update1s.connect(self.updateCoverLightGui)
        self.app.update1s.connect(self.updateDomeGui)
        self.app.update1s.connect(self.updateShutterStatGui)
        self.app.update1s.connect(self.updateImagingParam)

    def initConfig(self):
        """
        :return:
        """
        config = self.app.config['mainW']
        self.ui.expTime.setValue(config.get('expTime', 1))
        self.ui.binning.setValue(config.get('binning', 1))
        self.ui.expTimeN.setValue(config.get('expTimeN', 1))
        self.ui.binningN.setValue(config.get('binningN', 1))
        self.ui.subFrame.setValue(config.get('subFrame', 100))
        self.ui.focalLength.setValue(config.get('focalLength', 100))
        self.ui.aperture.setValue(config.get('aperture', 100))
        self.ui.focuserStepsize.setValue(config.get('focuserStepsize', 100))
        self.ui.focuserSteps.setValue(config.get('focuserSteps', 100))
        self.ui.fastDownload.setChecked(config.get('fastDownload', True))
        self.ui.keepModelImages.setChecked(config.get('keepModelImages', True))
        self.ui.keepAnalysisImages.setChecked(config.get('keepAnalysisImages', True))

        return True

    def storeConfig(self):
        """
        :return:
        """
        config = self.app.config['mainW']
        config['expTime'] = self.ui.expTime.value()
        config['binning'] = self.ui.binning.value()
        config['expTimeN'] = self.ui.expTimeN.value()
        config['binningN'] = self.ui.binningN.value()
        config['subFrame'] = self.ui.subFrame.value()
        config['focalLength'] = self.ui.focalLength.value()
        config['aperture'] = self.ui.aperture.value()
        config['focuserStepsize'] = self.ui.focuserStepsize.value()
        config['focuserSteps'] = self.ui.focuserSteps.value()
        config['fastDownload'] = self.ui.fastDownload.isChecked()
        config['keepModelImages'] = self.ui.keepModelImages.isChecked()
        config['keepAnalysisImages'] = self.ui.keepAnalysisImages.isChecked()
        return True

    def checkEnableCameraUI(self):
        """
        :return:
        """
        coolerTemp = self.app.camera.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')
        coolerPower = self.app.camera.data.get('CCD_COOLER_POWER.CCD_COOLER_VALUE')
        gainCam = self.app.camera.data.get('CCD_GAIN.GAIN')
        offsetCam = self.app.camera.data.get('CCD_OFFSET.OFFSET')
        humidityCCD = self.app.camera.data.get('CCD_HUMIDITY.HUMIDITY')
        coolerOn = self.app.camera.data.get('CCD_COOLER.COOLER_ON')
        downloadFast = self.app.camera.data.get('READOUT_QUALITY.QUALITY_LOW')
        pixelX = self.app.camera.data.get('CCD_INFO.CCD_MAX_X')

        enable = coolerTemp is not None
        self.ui.coolerTemp.setEnabled(enable)
        enable = coolerPower is not None
        self.ui.coolerPower.setEnabled(enable)
        enable = gainCam is not None
        self.ui.gainCam.setEnabled(enable)
        enable = offsetCam is not None
        self.ui.offsetCam.setEnabled(enable)
        enable = humidityCCD is not None
        self.ui.humidityCCD.setEnabled(enable)
        enable = coolerOn is not None
        self.ui.coolerOn.setEnabled(enable)
        self.ui.coolerOff.setEnabled(enable)
        enable = downloadFast is not None
        self.ui.downloadFast.setEnabled(enable)
        self.ui.downloadSlow.setEnabled(enable)
        enable = pixelX is not None
        self.ui.subFrame.setEnabled(enable)
        return True

    def updateGainOffset(self):
        """
        :return:
        """
        actValue = self.app.camera.data.get('CCD_OFFSET.OFFSET')
        offsetList = self.app.camera.data.get('CCD_OFFSET.OFFSET_LIST')
        if offsetList is not None and actValue is not None:
            offsetList = list(offsetList)
            self.guiSetText(self.ui.offsetCam, 's', offsetList[actValue])
        else:
            self.guiSetText(self.ui.offsetCam, '3.0f', actValue)

        actValue = self.app.camera.data.get('CCD_GAIN.GAIN')
        gainList = self.app.camera.data.get('CCD_GAIN.GAIN_LIST')
        if gainList is not None and actValue is not None:
            gainList = list(gainList)
            self.guiSetText(self.ui.gainCam, 's', gainList[actValue])
        else:
            self.guiSetText(self.ui.gainCam, '3.0f', actValue)

        return True

    def updateCooler(self):
        """
        :return:
        """
        coolerTemp = self.app.camera.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', 0)
        coolerPower = self.app.camera.data.get('CCD_COOLER_POWER.CCD_COOLER_VALUE', 0)
        coolerOn = self.app.camera.data.get('CCD_COOLER.COOLER_ON', False)
        self.guiSetText(self.ui.coolerTemp, '3.1f', coolerTemp)
        self.guiSetText(self.ui.coolerPower, '3.1f', coolerPower)
        if coolerOn:
            self.changeStyleDynamic(self.ui.coolerOn, 'running', True)
            self.changeStyleDynamic(self.ui.coolerOff, 'running', False)
        else:
            self.changeStyleDynamic(self.ui.coolerOn, 'running', False)
            self.changeStyleDynamic(self.ui.coolerOff, 'running', True)
        return True

    def updateFilter(self):
        """
        :return:
        """
        filterNumber = self.app.filter.data.get('FILTER_SLOT.FILTER_SLOT_VALUE', 1)
        key = f'FILTER_NAME.FILTER_SLOT_NAME_{filterNumber:1.0f}'
        filterName = self.app.filter.data.get(key, 'not found')
        self.guiSetText(self.ui.filterNumber, '1.0f', filterNumber)
        self.guiSetText(self.ui.filterName, 's', filterName)
        return True

    def updateFocuser(self):
        """
        :return:
        """
        focus = self.app.focuser.data.get('ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)
        self.guiSetText(self.ui.focuserPosition, '6.0f', focus)
        return True

    def updateImagingParam(self):
        """
        updateImagingParam reads the data from the classes and writes them to the gui.
        if a parameter is not set (no key entry) or None, the gui will show a '-'

        :return: true for test purpose
        """
        self.checkEnableCameraUI()
        self.updateGainOffset()
        self.updateCooler()
        self.updateFilter()
        self.updateFocuser()

        focalLength = self.ui.focalLength.value()
        aperture = self.ui.aperture.value()
        maxBinX = self.app.camera.data.get('CCD_BINNING.HOR_BIN_MAX', 9)
        maxBinY = self.app.camera.data.get('CCD_BINNING.HOR_BIN_MAX', 9)
        humidityCCD = self.app.camera.data.get('CCD_HUMIDITY.HUMIDITY')
        downloadFast = self.app.camera.data.get('READOUT_QUALITY.QUALITY_LOW', False)

        if maxBinX and maxBinY:
            maxBin = min(maxBinX, maxBinY)
            self.ui.binning.setMaximum(maxBin)
            self.ui.binningN.setMaximum(maxBin)

        self.app.camera.expTime = self.ui.expTime.value()
        self.app.camera.expTimeN = self.ui.expTimeN.value()
        self.app.camera.binning = self.ui.binning.value()
        self.app.camera.binningN = self.ui.binningN.value()
        self.app.camera.subFrame = self.ui.subFrame.value()
        self.app.camera.fastDownload = self.ui.fastDownload.isChecked()
        self.app.telescope.focalLength = focalLength
        self.app.telescope.aperture = aperture

        self.guiSetText(self.ui.humidityCCD, '3.1f', humidityCCD)

        if downloadFast:
            self.changeStyleDynamic(self.ui.downloadFast, 'running', True)
            self.changeStyleDynamic(self.ui.downloadSlow, 'running', False)
        else:
            self.changeStyleDynamic(self.ui.downloadFast, 'running', False)
            self.changeStyleDynamic(self.ui.downloadSlow, 'running', True)

        return True

    def setCoolerTemp(self):
        """
        :return: success
        """
        canSetCCDTemp = self.app.camera.data.get('CAN_SET_CCD_TEMPERATURE', False)
        if not canSetCCDTemp:
            return False

        actValue = self.app.camera.data.get(
            'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', None)
        if actValue is None:
            return False

        actValue = int(actValue)
        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self, 'Set cooler temperature', 'Value (-30..+20):',
            actValue, -30, 20, 1)
        if not ok:
            return False

        self.app.camera.sendCoolerTemp(temperature=value)
        return True

    def setOffset(self):
        """
        :return: success
        """
        actValue = self.app.camera.data.get('CCD_OFFSET.OFFSET', None)
        if actValue is None:
            return False

        actValue = int(actValue)
        dlg = QInputDialog()
        offsetList = self.app.camera.data.get('CCD_OFFSET.OFFSET_LIST')
        offsetMin = self.app.camera.data.get('CCD_OFFSET.OFFSET_MIN')
        offsetMax = self.app.camera.data.get('CCD_OFFSET.OFFSET_MAX')
        if offsetList is not None:
            offsetList = list(offsetList)
            value, ok = dlg.getItem(
                self, 'Set offset', 'Offset entry: ', offsetList, actValue)
            value = offsetList.index(value)

        elif offsetMin is not None and offsetMax is not None:
            offsetMin = int(offsetMin)
            offsetMax = int(offsetMax)
            value, ok = dlg.getInt(self,
                                   'Set offset',
                                   f'Values ({offsetMin:4}..{offsetMax:4}):',
                                   actValue, offsetMin, offsetMax,
                                   int((offsetMax - offsetMin) / 20))
        else:
            value, ok = dlg.getInt(self, 'Set offset', 'Values:', actValue)
        if not ok:
            return False

        self.app.camera.sendOffset(offset=value)
        return True

    def setGain(self):
        """
        :return: success
        """
        actValue = self.app.camera.data.get('CCD_GAIN.GAIN', None)
        if actValue is None:
            return False
        actValue = int(actValue)
        dlg = QInputDialog()
        gainList = self.app.camera.data.get('CCD_GAIN.GAIN_LIST')
        gainMin = self.app.camera.data.get('CCD_GAIN.GAIN_MIN')
        gainMax = self.app.camera.data.get('CCD_GAIN.GAIN_MAX')
        if gainList is not None:
            gainList = list(gainList)
            value, ok = dlg.getItem(
                self, 'Set gain', 'Gain entry: ', gainList, actValue)
            value = gainList.index(value)

        elif gainMin is not None and gainMax is not None:
            gainMin = int(gainMin)
            gainMax = int(gainMax)
            value, ok = dlg.getInt(
                self, 'Set gain', f'Values ({gainMin:4}..{gainMax:4}):',
                actValue, gainMin, gainMax, int((gainMax - gainMin) / 20))
        else:
            value, ok = dlg.getInt(self, 'Set gain', 'Values:', actValue)

        if not ok:
            return False

        self.app.camera.sendGain(gain=value)
        return True

    def setFilterNumber(self):
        """
        :return: success
        """
        data = self.app.filter.data
        actValue = data.get('FILTER_SLOT.FILTER_SLOT_VALUE')
        if actValue is None:
            return False
        actValue = int(actValue)

        availNames = list(data[key] for key in data if 'FILTER_NAME.FILTER_SLOT_NAME_' in key)
        numberFilter = len(availNames)
        isAlpaca = 'FILTER_NAME.FILTER_SLOT_NAME_0' in data
        if isAlpaca:
            start = 0
            end = numberFilter - 1
        else:
            start = 1
            end = numberFilter

        dlg = QInputDialog()
        value, ok = dlg.getInt(
            self, 'Set filter number', f'Value ({start}..{end}):',
            actValue, start, end, 1)
        if not ok:
            return False

        self.app.filter.sendFilterNumber(filterNumber=value)
        return True

    def setFilterName(self):
        """
        :return: success
        """
        data = self.app.filter.data
        actValue = data.get('FILTER_SLOT.FILTER_SLOT_VALUE')
        if actValue is None:
            return False
        actValue = int(actValue)

        availNames = list(data[key] for key in data if 'FILTER_NAME.FILTER_SLOT_NAME_' in key)

        dlg = QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set filter', 'Filter Name: ',
                                availNames, actValue - 1)
        self.log.debug(f'FilterSelected: [{value}], FilterList: [{availNames}]')
        if not ok:
            return False

        isAlpaca = 'FILTER_NAME.FILTER_SLOT_NAME_0' in data
        if isAlpaca:
            number = availNames.index(value)
        else:
            number = availNames.index(value) + 1

        self.app.filter.sendFilterNumber(filterNumber=number)
        return True

    def setDownloadModeFast(self):
        """
        :return:
        """
        self.app.camera.sendDownloadMode(fastReadout=True)
        return True

    def setDownloadModeSlow(self):
        """
        :return:
        """
        self.app.camera.sendDownloadMode(fastReadout=False)
        return True

    def setCoolerOn(self):
        """
        :return:
        """
        self.app.camera.sendCoolerSwitch(coolerOn=True)
        return True

    def setCoolerOff(self):
        """
        :return:
        """
        self.app.camera.sendCoolerSwitch(coolerOn=False)
        return True

    def updateCoverStatGui(self):
        """
        :return: True for test purpose
        """
        value = self.app.cover.data.get('CAP_PARK.PARK', None)
        if value:
            self.changeStyleDynamic(self.ui.coverPark, 'running', True)
            self.changeStyleDynamic(self.ui.coverUnpark, 'running', False)
        elif value is None:
            self.changeStyleDynamic(self.ui.coverPark, 'running', False)
            self.changeStyleDynamic(self.ui.coverUnpark, 'running', False)
        else:
            self.changeStyleDynamic(self.ui.coverPark, 'running', False)
            self.changeStyleDynamic(self.ui.coverUnpark, 'running', True)

        value = self.app.cover.data.get('Status.Cover', '-')
        self.ui.coverStatusText.setText(value)
        return True

    def updateCoverLightGui(self):
        """
        :return: True for test purpose
        """
        value = self.app.cover.data.get('FLAT_LIGHT_CONTROL.FLAT_LIGHT_ON', None)
        if value:
            self.changeStyleDynamic(self.ui.coverLightOn, 'running', True)
            self.changeStyleDynamic(self.ui.coverLightOff, 'running', False)
        elif value is None:
            self.changeStyleDynamic(self.ui.coverLightOn, 'running', False)
            self.changeStyleDynamic(self.ui.coverLightOff, 'running', False)
        else:
            self.changeStyleDynamic(self.ui.coverLightOn, 'running', False)
            self.changeStyleDynamic(self.ui.coverLightOff, 'running', True)

        value = self.app.cover.data.get(
            'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE')
        self.guiSetText(self.ui.coverLightIntensity, '3.0f', value)
        return True

    def setCoverPark(self):
        """
        :return: success
        """
        suc = self.app.cover.closeCover()
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Cover close could not be executed')
        return suc

    def setCoverUnpark(self):
        """
        :return: success
        """
        suc = self.app.cover.openCover()
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Cover open could not be executed')
        return suc

    def setCoverHalt(self):
        """
        :return: success
        """
        suc = self.app.cover.haltCover()
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Cover stop could not be executed')
        return suc

    def moveFocuserIn(self):
        """
        :return: success
        """
        pos = self.app.focuser.data.get('ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)
        step = self.ui.focuserSteps.value()
        newPos = pos - step
        suc = self.app.focuser.move(position=newPos)
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Focuser move in could not be executed')
        return suc

    def moveFocuserOut(self):
        """
        :return: success
        """
        pos = self.app.focuser.data.get('ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)
        step = self.ui.focuserSteps.value()
        newPos = pos + step
        suc = self.app.focuser.move(position=newPos)
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Focuser move out could not be executed')
        return suc

    def haltFocuser(self):
        """
        :return: success
        """
        suc = self.app.focuser.halt()
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Focuser halt could not be executed')
        return suc

    def switchLightOn(self):
        """
        :return:
        """
        suc = self.app.cover.lightOn()
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Light could not be switched on')
        return suc

    def switchLightOff(self):
        """
        :return:
        """
        suc = self.app.cover.lightOff()
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Light could not be switched off')
        return suc

    def setLightIntensity(self):
        """
        :return: success
        """
        actValue = self.app.cover.data.get(
            'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE')
        if actValue is None:
            return False

        dlg = QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set light intensity', 'Value (0..255):',
                               float(actValue), 0, 255, 1)
        if not ok:
            return False

        self.ui.coverLightIntensity.setText(f'{value}')
        suc = self.app.cover.lightIntensity(value)
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Light intensity could not be set')
        return suc

    def updateDomeGui(self):
        """
        :return: True for test purpose
        """
        value = self.app.dome.data.get('DOME_MOTION.DOME_CW', None)
        if value:
            self.changeStyleDynamic(self.ui.domeSlewCW, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.domeSlewCW, 'running', False)

        value = self.app.dome.data.get('DOME_MOTION.DOME_CCW', None)
        if value:
            self.changeStyleDynamic(self.ui.domeSlewCCW, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.domeSlewCCW, 'running', False)

        value = self.app.dome.data.get('ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION')
        self.guiSetText(self.ui.domeAzimuth, '3.0f', value)
        return True

    def updateShutterStatGui(self):
        """
        :return: True for test purpose
        """
        value = self.app.dome.data.get('DOME_SHUTTER.SHUTTER_OPEN', None)
        if value is True:
            self.changeStyleDynamic(self.ui.domeOpenShutter, 'running', True)
            self.changeStyleDynamic(self.ui.domeCloseShutter, 'running', False)
        elif value is False:
            self.changeStyleDynamic(self.ui.domeOpenShutter, 'running', False)
            self.changeStyleDynamic(self.ui.domeCloseShutter, 'running', True)
        else:
            self.changeStyleDynamic(self.ui.domeOpenShutter, 'running', False)
            self.changeStyleDynamic(self.ui.domeCloseShutter, 'running', False)

        value = self.app.dome.data.get('Status.Shutter', None)
        if value:
            self.ui.domeShutterStatusText.setText(value)
        return True

    def domeSlewCW(self):
        """
        :return:
        """
        if not self.deviceStat['dome']:
            return False

        suc = self.app.dome.slewCW()
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Dome could not be slewed CW')
        return suc

    def domeSlewCCW(self):
        """
        :return:
        """
        if not self.deviceStat['dome']:
            return False

        suc = self.app.dome.slewCCW()
        if not suc:
            self.msg.emit(2, 'Setting', 'Imaging',
                          'Dome could not be slewed CCW')
        return suc

    def domeAbortSlew(self):
        """
        :return:
        """
        if not self.deviceStat['dome']:
            return False

        suc = self.app.dome.abortSlew()
        if not suc:
            self.msg.emit(2, 'Dome', 'Command',
                          'Dome slew abort could not be executed')
        return suc

    def domeOpenShutter(self):
        """
        :return:
        """
        if not self.deviceStat['dome']:
            return False

        suc = self.app.dome.openShutter()
        if not suc:
            self.msg.emit(2, 'Dome', 'Command',
                          'Dome open shutter could not be executed')
        return suc

    def domeCloseShutter(self):
        """
        :return:
        """
        if not self.deviceStat['dome']:
            return False

        suc = self.app.dome.closeShutter()
        if not suc:
            self.msg.emit(2, 'Dome', 'Command',
                          'Dome close shutter could not be executed')
        return suc

    def domeMoveGameController(self, turnVal, openVal):
        """
        :param turnVal:
        :param openVal:
        :return:
        """
        if not self.deviceStat['dome']:
            return False

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
        return True
