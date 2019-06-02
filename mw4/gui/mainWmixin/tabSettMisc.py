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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
# external packages
import PyQt5.QtMultimedia
# local import


class SettMisc(object):
    """
    the SettMisc window class handles the settings misc menu. all necessary processing
    for functions of that gui will be linked to this class.
    """

    def __init__(self):

        self.audioSignalsSet = dict()
        self.guiAudioList = dict()

        self.setupAudioSignals()

        self.ui.loglevelDebug.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelInfo.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelWarning.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelError.clicked.connect(self.setLoggingLevel)
        self.ui.loglevelDebugIB.clicked.connect(self.setLoggingLevelIB)
        self.ui.loglevelInfoIB.clicked.connect(self.setLoggingLevelIB)
        self.ui.loglevelWarningIB.clicked.connect(self.setLoggingLevelIB)
        self.ui.loglevelErrorIB.clicked.connect(self.setLoggingLevelIB)
        self.ui.loglevelDebugMC.clicked.connect(self.setLoggingLevelMC)
        self.ui.loglevelInfoMC.clicked.connect(self.setLoggingLevelMC)
        self.ui.loglevelWarningMC.clicked.connect(self.setLoggingLevelMC)
        self.ui.loglevelErrorMC.clicked.connect(self.setLoggingLevelMC)

        self.app.mount.signals.alert.connect(self.playAudioMountAlert)
        self.app.dome.signals.slewFinished.connect(self.playAudioDomeSlewFinished)
        self.app.mount.signals.slewFinished.connect(self.playAudioMountSlewFinished)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        self.ui.loglevelDebug.setChecked(config.get('loglevelDebug', True))
        self.ui.loglevelInfo.setChecked(config.get('loglevelInfo', False))
        self.ui.loglevelWarning.setChecked(config.get('loglevelWarning', False))
        self.ui.loglevelError.setChecked(config.get('loglevelError', False))

        self.ui.loglevelDebugIB.setChecked(config.get('loglevelDebugIB', True))
        self.ui.loglevelInfoIB.setChecked(config.get('loglevelInfoIB', False))
        self.ui.loglevelWarningIB.setChecked(config.get('loglevelWarningIB', False))
        self.ui.loglevelErrorIB.setChecked(config.get('loglevelErrorIB', False))

        self.ui.loglevelDebugMC.setChecked(config.get('loglevelDebugMC', True))
        self.ui.loglevelInfoMC.setChecked(config.get('loglevelInfoMC', False))
        self.ui.loglevelWarningMC.setChecked(config.get('loglevelWarningMC', False))
        self.ui.loglevelErrorMC.setChecked(config.get('loglevelErrorMC', False))

        self.setLoggingLevel()
        self.setLoggingLevelIB()
        self.setLoggingLevelMC()

        self.ui.expiresYes.setChecked(config.get('expiresYes', True))
        self.ui.expiresNo.setChecked(config.get('expiresNo', False))

        self.setupAudioGui()
        self.ui.soundMountSlewFinished.setCurrentIndex(config.get('soundMountSlewFinished', 0))
        self.ui.soundDomeSlewFinished.setCurrentIndex(config.get('soundDomeSlewFinished', 0))
        self.ui.soundMountAlert.setCurrentIndex(config.get('soundMountAlert', 0))
        self.ui.soundModelingFinished.setCurrentIndex(config.get('soundModelingFinished', 0))

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['loglevelDebug'] = self.ui.loglevelDebug.isChecked()
        config['loglevelInfo'] = self.ui.loglevelInfo.isChecked()
        config['loglevelWarning'] = self.ui.loglevelWarning.isChecked()
        config['loglevelError'] = self.ui.loglevelError.isChecked()

        config['loglevelDebugIB'] = self.ui.loglevelDebugIB.isChecked()
        config['loglevelInfoIB'] = self.ui.loglevelInfoIB.isChecked()
        config['loglevelWarningIB'] = self.ui.loglevelWarningIB.isChecked()
        config['loglevelErrorIB'] = self.ui.loglevelErrorIB.isChecked()

        config['loglevelDebugMC'] = self.ui.loglevelDebugMC.isChecked()
        config['loglevelInfoMC'] = self.ui.loglevelInfoMC.isChecked()
        config['loglevelWarningMC'] = self.ui.loglevelWarningMC.isChecked()
        config['loglevelErrorMC'] = self.ui.loglevelErrorMC.isChecked()

        config['expiresYes'] = self.ui.expiresYes.isChecked()
        config['expiresNo'] = self.ui.expiresNo.isChecked()

        config['soundMountSlewFinished'] = self.ui.soundMountSlewFinished.currentIndex()
        config['soundDomeSlewFinished'] = self.ui.soundDomeSlewFinished.currentIndex()
        config['soundMountAlert'] = self.ui.soundMountAlert.currentIndex()
        config['soundModelingFinished'] = self.ui.soundModelingFinished.currentIndex()

        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """
        return True

    def updateFwGui(self, fw):
        """
        updateFwGui write all firmware data to the gui.

        :return:    True if ok for testing
        """

        if fw.productName is not None:
            self.ui.productName.setText(fw.productName)
        else:
            self.ui.productName.setText('-')

        if fw.numberString is not None:
            self.ui.numberString.setText(fw.numberString)
        else:
            self.ui.numberString.setText('-')

        if fw.fwdate is not None:
            self.ui.fwdate.setText(fw.fwdate)
        else:
            self.ui.fwdate.setText('-')

        if fw.fwtime is not None:
            self.ui.fwtime.setText(fw.fwtime)
        else:
            self.ui.fwtime.setText('-')

        if fw.hwVersion is not None:
            self.ui.hwVersion.setText(fw.hwVersion)
        else:
            self.ui.hwVersion.setText('-')

        return True

    def setLoggingLevel(self):
        """
        Setting the log level according to the setting in the gui.

        :return: nothing
        """

        if self.ui.loglevelDebug.isChecked():
            logging.getLogger().setLevel(logging.DEBUG)
        elif self.ui.loglevelInfo.isChecked():
            logging.getLogger().setLevel(logging.INFO)
        elif self.ui.loglevelWarning.isChecked():
            logging.getLogger().setLevel(logging.WARNING)
        elif self.ui.loglevelError.isChecked():
            logging.getLogger().setLevel(logging.ERROR)

    def setLoggingLevelIB(self):
        """
        Setting the log level according to the setting in the gui.

        :return: nothing
        """

        if self.ui.loglevelDebugIB.isChecked():
            logging.getLogger('indibase').setLevel(logging.DEBUG)
        elif self.ui.loglevelInfoIB.isChecked():
            logging.getLogger('indibase').setLevel(logging.INFO)
        elif self.ui.loglevelWarningIB.isChecked():
            logging.getLogger('indibase').setLevel(logging.WARNING)
        elif self.ui.loglevelErrorIB.isChecked():
            logging.getLogger('indibase').setLevel(logging.ERROR)

    def setLoggingLevelMC(self):
        """
        Setting the log level according to the setting in the gui.

        :return: nothing
        """

        if self.ui.loglevelDebugMC.isChecked():
            logging.getLogger('mountcontrol').setLevel(logging.DEBUG)
        elif self.ui.loglevelInfoMC.isChecked():
            logging.getLogger('mountcontrol').setLevel(logging.INFO)
        elif self.ui.loglevelWarningMC.isChecked():
            logging.getLogger('mountcontrol').setLevel(logging.WARNING)
        elif self.ui.loglevelErrorMC.isChecked():
            logging.getLogger('mountcontrol').setLevel(logging.ERROR)

    def setupAudioGui(self):
        """
        setupAudioGui populates the audio selection gui

        :return: True for test purpose
        """

        self.guiAudioList['MountSlew'] = self.ui.soundMountSlewFinished
        self.guiAudioList['DomeSlew'] = self.ui.soundDomeSlewFinished
        self.guiAudioList['MountAlert'] = self.ui.soundMountAlert
        self.guiAudioList['ModelingFinished'] = self.ui.soundModelingFinished

        for itemKey, itemValue in self.guiAudioList.items():
            self.guiAudioList[itemKey].addItem('None')
            self.guiAudioList[itemKey].addItem('Beep')
            self.guiAudioList[itemKey].addItem('Horn')
            self.guiAudioList[itemKey].addItem('Beep1')
            self.guiAudioList[itemKey].addItem('Alarm')
            self.guiAudioList[itemKey].addItem('Alert')
        return True

    def setupAudioSignals(self):
        """
        setupAudioSignals pre loads all know audio signals for events handling

        :return: True for test purpose
        """

        self.audioSignalsSet['Beep'] = PyQt5.QtMultimedia.QSound(':/beep.wav')
        self.audioSignalsSet['Alert'] = PyQt5.QtMultimedia.QSound(':/alert.wav')
        self.audioSignalsSet['Horn'] = PyQt5.QtMultimedia.QSound(':/horn.wav')
        self.audioSignalsSet['Beep1'] = PyQt5.QtMultimedia.QSound(':/beep1.wav')
        self.audioSignalsSet['Alarm'] = PyQt5.QtMultimedia.QSound(':/alarm.wav')
        return True

    def playAudioMountSlewFinished(self):
        """
        playAudioMountSlewFinished plays a defined sound if this events happens

        :return: success of playing sound
        """

        listEntry = self.guiAudioList.get('MountSlew', None)
        if listEntry is None:
            return False
        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            self.audioSignalsSet[sound].play()
        return True

    def playAudioDomeSlewFinished(self):
        """
        playAudioDomeSlewFinished plays a defined sound if this events happens

        :return: success of playing sound
        """

        listEntry = self.guiAudioList.get('DomeSlew', None)
        if listEntry is None:
            return False
        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            self.audioSignalsSet[sound].play()
        return True

    def playAudioMountAlert(self):
        """
        playAudioMountAlert plays a defined sound if this events happens

        :return: success of playing sound
        """

        listEntry = self.guiAudioList.get('MountAlert', None)
        if listEntry is None:
            return False
        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            self.audioSignalsSet[sound].play()
        return True

    def playAudioModelFinished(self):
        """
        playAudioModelFinished plays a defined sound if this events happens

        :return: success of playing sound
        """

        listEntry = self.guiAudioList.get('ModelingFinished', None)
        if listEntry is None:
            return False
        sound = listEntry.currentText()
        if sound in self.audioSignalsSet:
            self.audioSignalsSet[sound].play()
        return True
