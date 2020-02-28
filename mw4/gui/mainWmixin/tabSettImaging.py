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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
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

    def __init__(self):
        # gui actions
        self.ui.downloadFast.clicked.connect(self.setDownloadModeFast)
        self.ui.downloadSlow.clicked.connect(self.setDownloadModeSlow)
        self.ui.coolerOn.clicked.connect(self.setCoolerOn)
        self.ui.coolerOff.clicked.connect(self.setCoolerOff)
        self.clickable(self.ui.coolerTemp).connect(self.setCoolerTemp)
        self.clickable(self.ui.filterNumber).connect(self.setFilterNumber)
        self.clickable(self.ui.filterName).connect(self.setFilterName)

        # cyclic actions
        self.app.update1s.connect(self.updateParameters)

    def initConfig(self):
        """

        :return:
        """

        config = self.app.config['mainW']
        self.ui.expTime.setValue(config.get('expTime', 1))
        self.ui.binning.setValue(config.get('binning', 1))
        self.ui.subFrame.setValue(config.get('subFrame', 100))
        self.ui.subFrame.setValue(config.get('subFrame', 100))
        self.ui.subFrame.setValue(config.get('subFrame', 100))
        self.ui.checkFastDownload.setChecked(config.get('checkFastDownload', False))
        self.ui.checkKeepImages.setChecked(config.get('checkKeepImages', False))
        self.ui.searchRadius.setValue(config.get('searchRadius', 2))
        self.ui.solveTimeout.setValue(config.get('solveTimeout', 30))

        return True

    def storeConfig(self):
        """

        :return:
        """

        config = self.app.config['mainW']
        config['expTime'] = self.ui.expTime.value()
        config['binning'] = self.ui.binning.value()
        config['subFrame'] = self.ui.subFrame.value()
        config['searchRadius'] = self.ui.searchRadius.value()
        config['solveTimeout'] = self.ui.solveTimeout.value()
        config['checkFastDownload'] = self.ui.checkFastDownload.isChecked()
        config['checkKeepImages'] = self.ui.checkKeepImages.isChecked()

        return True

    @staticmethod
    def guiSetText(ui, formatElement, value):
        """

        :param ui:
        :param formatElement:
        :param value:
        :return:
        """
        if value is None:
            text = '-'
        else:
            formatStr = '{0:' + formatElement + '}'
            text = formatStr.format(value)
        ui.setText(text)

    def updateParameters(self):
        """

        :return: success
        """

        focalLength = self.app.telescope.data.get('TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH', 0)
        aperture = self.app.telescope.data.get('TELESCOPE_INFO.TELESCOPE_APERTURE', 0)
        pixelSizeX = self.app.camera.data.get('CCD_INFO.CCD_PIXEL_SIZE_X', 0)
        pixelSizeY = self.app.camera.data.get('CCD_INFO.CCD_PIXEL_SIZE_Y', 0)
        pixelX = self.app.camera.data.get('CCD_INFO.CCD_MAX_X', 0)
        pixelY = self.app.camera.data.get('CCD_INFO.CCD_MAX_Y', 0)
        rotation = self.app.camera.data.get('CCD_ROTATION.CCD_ROTATION_VALUE', 0)
        coolerTemp = self.app.camera.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE', 0)
        coolerPower = self.app.camera.data.get('CCD_COOLER_POWER.CCD_COOLER_VALUE', 0)
        coolerOn = self.app.camera.data.get('CCD_COOLER.COOLER_ON', False)
        downloadFast = self.app.camera.data.get('READOUT_QUALITY.QUALITY_LOW', False)
        focus = self.app.focuser.data.get('ABS_FOCUS_POSITION.FOCUS_ABSOLUTE_POSITION', 0)
        filterNumber = self.app.camera.data.get('FILTER_SLOT.FILTER_SLOT_VALUE', 1)

        key = f'FILTER_NAME.FILTER_SLOT_NAME_{filterNumber:1.0f}'
        text = self.app.camera.data.get(key, 'not found')
        self.guiSetText(self.ui.filterName, 's', text)
        self.guiSetText(self.ui.focalLength, '4.0f', focalLength)
        self.guiSetText(self.ui.aperture, '3.0f', aperture)
        self.guiSetText(self.ui.pixelSizeX, '2.2f', pixelSizeX)
        self.guiSetText(self.ui.pixelSizeY, '2.2f', pixelSizeY)
        self.guiSetText(self.ui.pixelX, '5.0f', pixelX)
        self.guiSetText(self.ui.pixelY, '5.0f', pixelY)
        self.guiSetText(self.ui.rotation, '3.1f', rotation)
        self.guiSetText(self.ui.filterNumber, '1.0f', filterNumber)
        self.guiSetText(self.ui.coolerTemp, '3.1f', coolerTemp)
        self.guiSetText(self.ui.coolerPower, '3.1f', coolerPower)
        self.guiSetText(self.ui.focuserPosition, '6.0f', focus)

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

        if focalLength and pixelSizeX and pixelSizeY:
            resolutionX = pixelSizeX / focalLength * 206.265
            resolutionY = pixelSizeY / focalLength * 206.265
        else:
            resolutionX = 0
            resolutionY = 0
        self.app.mainW.ui.resolutionX.setText(f'{resolutionX:2.2f}')
        self.app.mainW.ui.resolutionY.setText(f'{resolutionY:2.2f}')

        if aperture:
            speed = focalLength / aperture
        else:
            speed = 0
        self.app.mainW.ui.speed.setText(f'{speed:2.1f}')

        if aperture:
            dawes = 116 / aperture
            rayleigh = 138 / aperture
            magLimit = 7.7 + (5 * np.log10(aperture / 10))
        else:
            dawes = 0
            rayleigh = 0
            magLimit = 0

        self.app.mainW.ui.dawes.setText(f'{dawes:2.2f}')
        self.app.mainW.ui.rayleigh.setText(f'{rayleigh:2.2f}')
        self.app.mainW.ui.magLimit.setText(f'{magLimit:2.2f}')

        if focalLength and pixelSizeY and pixelSizeY and pixelX and pixelY:
            FOVX = pixelSizeX / focalLength * 206.265 * pixelX / 3600
            FOVY = pixelSizeY / focalLength * 206.265 * pixelY / 3600
        else:
            FOVX = 0
            FOVY = 0
        self.app.mainW.ui.FOVX.setText(f'{FOVX:2.2f}')
        self.app.mainW.ui.FOVY.setText(f'{FOVY:2.2f}')

    def setCoolerTemp(self):
        """
        setCoolerTemp sends the desired cooler temp and switches the cooler on.
        setting

        :return: success
        """

        msg = PyQt5.QtWidgets.QMessageBox
        actValue = self.app.camera.data.get('CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE')

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

    def setFilterNumber(self):
        """
        setFilterNumber sends the desired filter number.
        setting

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

        availNames = list(data[key] for key in data if 'FILTER_SLOT_NAME_' in key)
        numberFilter = len(availNames)

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getInt(self,
                               'Set filter number',
                               f'Value (1..{numberFilter}):',
                               actValue,
                               1,
                               numberFilter,
                               1,
                               )

        if not ok:
            return False

        self.app.filter.sendFilterNumber(filterNumber=value)

        return True

    def setFilterName(self):
        """
        setFilterName sends the desired filter name
        setting

        :return: success
        """

        msg = PyQt5.QtWidgets.QMessageBox
        data = self.app.camera.data

        actValue = data.get('FILTER_SLOT.FILTER_SLOT_VALUE')
        if actValue is None:
            msg.critical(self,
                         'Error Message',
                         'Value cannot be set when not connected !')
            return False

        availNames = list(data[key] for key in data if 'FILTER_SLOT_NAME_' in key)

        dlg = PyQt5.QtWidgets.QInputDialog()
        value, ok = dlg.getItem(self,
                                'Set filter',
                                'Filter Name: ',
                                availNames,
                                actValue - 1,
                                )

        if not ok:
            return False

        number = availNames.index(value) + 1
        self.app.filter.sendFilterNumber(filterNumber=number)

        return True

    def setDownloadModeFast(self):
        """
        setDownloadModeFast set the download speed high for image download.

        :return:
        """

        self.app.camera.sendDownloadMode(fastReadout=True)

        return True

    def setDownloadModeSlow(self):
        """
        setDownloadModeSlow set the download speed low for image download.

        :return:
        """

        self.app.camera.sendDownloadMode(fastReadout=False)

        return True

    def setCoolerOn(self):
        """
        setCoolerOn set the on

        :return:
        """

        self.app.camera.sendCoolerSwitch(coolerOn=True)

        return True

    def setCoolerOff(self):
        """
        setCoolerOff set the off

        :return:
        """

        self.app.camera.sendCoolerSwitch(coolerOn=False)

        return True
