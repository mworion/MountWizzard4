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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5
import numpy as np

# local import


class SettImaging(object):
    """
    """

    def __init__(self, app=None, ui=None, clickable=None):
        if app:
            self.app = app
            self.ui = ui
            self.clickable = clickable

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
        self.ui.coverHalt.clicked.connect(self.setCoverHalt)
        self.ui.coverLightOn.clicked.connect(self.switchLightOn)
        self.ui.coverLightOff.clicked.connect(self.switchLightOff)
        self.clickable(self.ui.coverLightIntensity).connect(self.setLightIntensity)
        self.ui.copyFromTelescopeDriver.clicked.connect(self.updateTelescopeParametersToGui)
        self.ui.aperture.valueChanged.connect(self.updateParameters)
        self.ui.focalLength.valueChanged.connect(self.updateParameters)
        self.ui.expTime.valueChanged.connect(self.updateParameters)
        self.ui.binning.valueChanged.connect(self.updateParameters)
        self.ui.expTimeN.valueChanged.connect(self.updateParameters)
        self.ui.binningN.valueChanged.connect(self.updateParameters)
        self.ui.subFrame.valueChanged.connect(self.updateParameters)
        self.ui.haltFocuser.clicked.connect(self.haltFocuser)
        self.ui.moveFocuserIn.clicked.connect(self.moveFocuserIn)
        self.ui.moveFocuserOut.clicked.connect(self.moveFocuserOut)
        self.app.update1s.connect(self.updateCoverStatGui)
        self.app.update1s.connect(self.updateCoverLightGui)
        self.app.update1s.connect(self.updateParameters)

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
        self.ui.checkFastDownload.setChecked(config.get('checkFastDownload', False))
        self.ui.checkKeepImages.setChecked(config.get('checkKeepImages', False))
        self.ui.checkAutomaticTelescope.setChecked(config.get('checkAutomaticTelescope', False))
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
        config['checkFastDownload'] = self.ui.checkFastDownload.isChecked()
        config['checkKeepImages'] = self.ui.checkKeepImages.isChecked()
        config['checkAutomaticTelescope'] = self.ui.checkAutomaticTelescope.isChecked()
        return True

    def updateParameters(self):
        """
        updateParameters reads the data from the classes and writes them to the gui.
        if a parameter is not set (no key entry) or None, the gui will show a '-'

        :return: true for test purpose
        """
        if self.ui.checkAutomaticTelescope.isChecked():
            self.updateTelescopeParametersToGui()

        focalLength = self.ui.focalLength.value()
        aperture = self.ui.aperture.value()
        pixelSizeX = self.app.camera.data.get('CCD_INFO.CCD_PIXEL_SIZE_X', 0)
        pixelSizeY = self.app.camera.data.get('CCD_INFO.CCD_PIXEL_SIZE_Y', 0)
        pixelX = self.app.camera.data.get('CCD_INFO.CCD_MAX_X', 0)
        pixelY = self.app.camera.data.get('CCD_INFO.CCD_MAX_Y', 0)
        maxBinX = self.app.camera.data.get('CCD_BINNING.HOR_BIN_MAX', 9)
        maxBinY = self.app.camera.data.get('CCD_BINNING.HOR_BIN_MAX', 9)
        rotation = self.app.camera.data.get('CCD_ROTATION.CCD_ROTATION_VALUE', 0)
        coolerTemp = self.app.camera.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', 0)
        coolerPower = self.app.camera.data.get('CCD_COOLER_POWER.CCD_COOLER_VALUE', 0)
        gainCam = self.app.camera.data.get('CCD_GAIN.GAIN')
        offsetCam = self.app.camera.data.get('CCD_OFFSET.OFFSET')
        humidityCCD = self.app.camera.data.get('CCD_HUMIDITY.HUMIDITY')
        coolerOn = self.app.camera.data.get('CCD_COOLER.COOLER_ON', False)
        downloadFast = self.app.camera.data.get('READOUT_QUALITY.QUALITY_LOW', False)
        focus = self.app.focuser.data.get('ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)
        filterNumber = self.app.filter.data.get('FILTER_SLOT.FILTER_SLOT_VALUE', 1)

        if maxBinX and maxBinY:
            maxBin = min(maxBinX, maxBinY)
            self.ui.binning.setMaximum(maxBin)
            self.ui.binningN.setMaximum(maxBin)

        self.app.camera.expTime = self.ui.expTime.value()
        self.app.camera.expTimeN = self.ui.expTimeN.value()
        self.app.camera.binning = self.ui.binning.value()
        self.app.camera.binningN = self.ui.binningN.value()
        self.app.camera.subFrame = self.ui.subFrame.value()
        self.app.camera.checkFastDownload = self.ui.checkFastDownload.isChecked()
        self.app.telescope.focalLength = focalLength
        self.app.telescope.aperture = aperture

        key = f'FILTER_NAME.FILTER_SLOT_NAME_{filterNumber:1.0f}'
        filterName = self.app.filter.data.get(key, 'not found')

        if focalLength and pixelSizeX and pixelSizeY:
            resolutionX = pixelSizeX / focalLength * 206.265
            resolutionY = pixelSizeY / focalLength * 206.265
        else:
            resolutionX = None
            resolutionY = None

        if aperture:
            speed = focalLength / aperture
        else:
            speed = None

        if aperture:
            dawes = 116 / aperture
            rayleigh = 138 / aperture
            magLimit = 7.7 + (5 * np.log10(aperture / 10))
        else:
            dawes = None
            rayleigh = None
            magLimit = None

        if focalLength and pixelSizeY and pixelSizeY and pixelX and pixelY:
            FOVX = pixelSizeX / focalLength * 206.265 * pixelX / 3600
            FOVY = pixelSizeY / focalLength * 206.265 * pixelY / 3600
        else:
            FOVX = None
            FOVY = None

        self.guiSetText(self.ui.filterNumber, '1.0f', filterNumber)
        self.guiSetText(self.ui.filterName, 's', filterName)
        self.guiSetText(self.ui.speed, '2.1f', speed)
        self.guiSetText(self.ui.pixelSizeX, '2.2f', pixelSizeX)
        self.guiSetText(self.ui.pixelSizeY, '2.2f', pixelSizeY)
        self.guiSetText(self.ui.pixelX, '5.0f', pixelX)
        self.guiSetText(self.ui.pixelY, '5.0f', pixelY)
        self.guiSetText(self.ui.rotation, '3.1f', rotation)
        self.guiSetText(self.ui.humidityCCD, '3.2f', humidityCCD)
        self.guiSetText(self.ui.coolerTemp, '3.1f', coolerTemp)
        self.guiSetText(self.ui.coolerPower, '3.1f', coolerPower)
        self.guiSetText(self.ui.gainCam, '3.0f', gainCam)
        self.guiSetText(self.ui.offsetCam, '3.0f', offsetCam)
        self.guiSetText(self.ui.focuserPosition, '6.0f', focus)
        self.guiSetText(self.ui.resolutionX, '2.2f', resolutionX)
        self.guiSetText(self.ui.resolutionY, '2.2f', resolutionY)
        self.guiSetText(self.ui.dawes, '2.2f', dawes)
        self.guiSetText(self.ui.rayleigh, '2.2f', rayleigh)
        self.guiSetText(self.ui.magLimit, '2.2f', magLimit)
        self.guiSetText(self.ui.FOVX, '2.2f', FOVX)
        self.guiSetText(self.ui.FOVY, '2.2f', FOVY)

        if coolerOn:
            self.changeStyleDynamic(self.ui.coolerOn, 'running', True)
            self.changeStyleDynamic(self.ui.coolerOff, 'running', False)
        else:
            self.changeStyleDynamic(self.ui.coolerOn, 'running', False)
            self.changeStyleDynamic(self.ui.coolerOff, 'running', True)

        if downloadFast:
            self.changeStyleDynamic(self.ui.downloadFast, 'running', True)
            self.changeStyleDynamic(self.ui.downloadSlow, 'running', False)
        else:
            self.changeStyleDynamic(self.ui.downloadFast, 'running', False)
            self.changeStyleDynamic(self.ui.downloadSlow, 'running', True)

        return True

    def updateTelescopeParametersToGui(self):
        """
        updateTelescopeParametersToGui takes the information gathered from the
        driver and programs them into gui for later use.

        :return: true for test purpose
        """
        value = self.app.telescope.data.get('TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH', 0)
        if value is not None:
            value = float(value)
            self.ui.focalLength.setValue(value)

        value = self.app.telescope.data.get('TELESCOPE_INFO.TELESCOPE_APERTURE', 0)
        if value is not None:
            value = float(value)
            self.ui.aperture.setValue(value)

        return True

    def setCoolerTemp(self):
        """
        :return: success
        """
        canSetCCDTemp = self.app.camera.data.get('CAN_SET_CCD_TEMPERATURE', False)
        if not canSetCCDTemp:
            return False

        msg = PyQt5.QtWidgets.QMessageBox
        actValue = self.app.camera.data.get(
            'CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', None)
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set cooler temperature',
                               'Value (-20..+20):',
                               actValue,
                               -20,
                               20,
                               1,
                               )
        if not ok:
            return False

        self.app.camera.sendCoolerTemp(temperature=value)
        return True

    def setOffset(self):
        """
        :return: success
        """
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = self.app.camera.data.get('CCD_OFFSET.OFFSET', None)
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set offset',
                               'Value (0..255):',
                               actValue,
                               0,
                               255,
                               1,
                               )
        if not ok:
            return False

        self.app.camera.sendOffset(offset=value)
        return True

    def setGain(self):
        """
        :return: success
        """
        msg = PyQt5.QtWidgets.QMessageBox
        minGain = self.app.camera.data.get('CCD_INFO.GAIN_MIN', 1)
        maxGain = self.app.camera.data.get('CCD_INFO.GAIN_MAX', 200)
        actValue = self.app.camera.data.get('CCD_GAIN.GAIN', None)
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set gain',
                               'Value (0..255):',
                               actValue,
                               minGain,
                               maxGain,
                               1,
                               )
        if not ok:
            return False

        self.app.camera.sendGain(gain=value)
        return True

    def setFilterNumber(self):
        """
        :return: success
        """
        msg = PyQt5.QtWidgets.QMessageBox
        data = self.app.filter.data

        actValue = data.get('FILTER_SLOT.FILTER_SLOT_VALUE')
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when not connected !')
            return False

        availNames = list(data[key] for key in data if 'FILTER_NAME.FILTER_SLOT_NAME_' in key)
        numberFilter = len(availNames)
        isAlpaca = 'FILTER_NAME.FILTER_SLOT_NAME_0' in data
        if isAlpaca:
            start = 0
            end = numberFilter - 1
        else:
            start = 1
            end = numberFilter

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set filter number',
                               f'Value ({start}..{end}):',
                               actValue,
                               start,
                               end,
                               1,
                               )

        if not ok:
            return False

        self.app.filter.sendFilterNumber(filterNumber=value)
        return True

    def setFilterName(self):
        """
        :return: success
        """
        msg = PyQt5.QtWidgets.QMessageBox
        data = self.app.filter.data

        actValue = data.get('FILTER_SLOT.FILTER_SLOT_VALUE')
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when not connected !')
            return False

        availNames = list(data[key] for key in data if 'FILTER_NAME.FILTER_SLOT_NAME_' in key)

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set filter',
                                'Filter Name: ',
                                availNames,
                                actValue - 1,
                                )
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
            self.app.message.emit('Cover close could not be executed', 2)
        return suc

    def setCoverUnpark(self):
        """
        :return: success
        """
        suc = self.app.cover.openCover()
        if not suc:
            self.app.message.emit('Cover open could not be executed', 2)
        return suc

    def setCoverHalt(self):
        """
        :return: success
        """
        suc = self.app.cover.haltCover()
        if not suc:
            self.app.message.emit('Cover stop could not be executed', 2)
        return suc

    def moveFocuserIn(self):
        """
        :return: success
        """
        pos = self.app.focuser.data.get('ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)
        step = self.ui.focuserStepsize.value()
        newPos = pos - step
        suc = self.app.focuser.move(position=newPos)
        if not suc:
            self.app.message.emit('Focuser move in could not be executed', 2)
        return suc

    def moveFocuserOut(self):
        """
        :return: success
        """
        pos = self.app.focuser.data.get('ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)
        step = self.ui.focuserStepsize.value()
        newPos = pos + step
        suc = self.app.focuser.move(position=newPos)
        if not suc:
            self.app.message.emit('Focuser move out could not be executed', 2)
        return suc

    def haltFocuser(self):
        """
        :return: success
        """
        suc = self.app.focuser.halt()
        if not suc:
            self.app.message.emit('Light could not be switched on', 2)
        return suc

    def switchLightOn(self):
        """
        :return:
        """
        suc = self.app.cover.lightOn()
        if not suc:
            self.app.message.emit('Light could not be switched on', 2)
        return suc

    def switchLightOff(self):
        """
        :return:
        """
        suc = self.app.cover.lightOff()
        if not suc:
            self.app.message.emit('Light could not be switched off', 2)
        return suc

    def setLightIntensity(self):
        """
        :return: success
        """
        msg = PyQt5.QtWidgets.QMessageBox
        actValue = self.app.cover.data.get(
            'FLAT_LIGHT_INTENSITY.FLAT_LIGHT_INTENSITY_VALUE')
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when not connected !')
            return False
        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set light intensity',
                               'Value (0..255):',
                               float(actValue),
                               0,
                               255,
                               1,
                               )
        if not ok:
            return False

        self.ui.coverLightIntensity.setText(f'{value}')
        suc = self.app.cover.lightIntensity(value)
        if not suc:
            self.app.message.emit('Light intensity could not be set', 2)

        return suc
