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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
from pathlib import Path
# external packages
import PyQt5
from astropy.io import fits
# local import


class Tools(object):
    """
    the main window class handles the main menu as well as the show and no show part of
    any other window. all necessary processing for functions of that gui will be linked
    to this class. therefore window classes will have a threadpool for managing async
    processing if needed.
    """

    def __init__(self):
        self.selectorsDropDowns = {'rename1': self.ui.rename1,
                                   'rename2': self.ui.rename2,
                                   'rename3': self.ui.rename3,
                                   'rename4': self.ui.rename4,
                                   'rename5': self.ui.rename5,
                                   }
        self.fitsHeaderKeywords = {'None': [''],
                                   'Text': ['RenameText'],
                                   'Datetime': ['DATE-OBS'],
                                   'Frame': ['FRAME', 'IMAGETYP'],
                                   'Filter': ['FILTER'],
                                   'Binning': ['XBINNING'],
                                   'Exp Time': ['EXPTIME'],
                                   'CCD Temp': ['CCD-TEMP'],
                                   }
        self.slewSpeeds = {'max': self.ui.slewSpeedMax,
                           'high': self.ui.slewSpeedHigh,
                           'med': self.ui.slewSpeedMed,
                           'low': self.ui.slewSpeedLow,
                           }
        self.slewSpeedFuncs = {'max': self.app.mount.setting.setSlewSpeedMax,
                               'high': self.app.mount.setting.setSlewSpeedHigh,
                               'med': self.app.mount.setting.setSlewSpeedMed,
                               'low': self.app.mount.setting.setSlewSpeedLow,
                               }
        self.slewSpeedSelected = None

        self.setupSelectorGui()

        # matching gui signals
        self.ui.renameStart.clicked.connect(self.renameRunGUI)
        self.ui.renameInputSelect.clicked.connect(self.chooseDir)
        self.ui.stopMoveAll.clicked.connect(self.stopMoveAll)
        self.ui.moveNorth.clicked.connect(self.moveNorth)
        self.ui.moveEast.clicked.connect(self.moveEast)
        self.ui.moveSouth.clicked.connect(self.moveSouth)
        self.ui.moveWest.clicked.connect(self.moveWest)
        self.ui.moveNorthWest.clicked.connect(self.moveNorthWest)
        self.ui.moveNorthEast.clicked.connect(self.moveNorthEast)
        self.ui.moveSouthEast.clicked.connect(self.moveSouthEast)
        self.ui.moveSouthWest.clicked.connect(self.moveSouthWest)
        self.ui.slewSpeedMax.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedHigh.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedMed.clicked.connect(self.setSlewSpeed)
        self.ui.slewSpeedLow.clicked.connect(self.setSlewSpeed)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        defaultDir = self.app.mwGlob['imageDir']
        self.ui.renameDir.setText(config.get('renameDir', defaultDir))
        self.ui.renameText.setText(config.get('renameText', ''))
        self.ui.checkIncludeSubdirs.setChecked(config.get('checkIncludeSubdirs', False))
        for name, ui in self.selectorsDropDowns.items():
            ui.setCurrentIndex(config.get(name, 0))

        self.ui.renameProgress.setValue(0)

        key = config.get('slewSpeed', 'high')
        self.slewSpeedSelected = key
        self.changeStyleDynamic(self.slewSpeeds[key], 'running', True)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        config = self.app.config['mainW']
        config['renameDir'] = self.ui.renameDir.text()
        config['renameText'] = self.ui.renameText.text()
        config['checkIncludeSubdirs'] = self.ui.checkIncludeSubdirs.isChecked()
        for name, ui in self.selectorsDropDowns.items():
            config[name] = ui.currentIndex()
        config['slewSpeed'] = self.slewSpeedSelected
        return True

    def setupSelectorGui(self):
        """
        setupSelectorGui handles the dropdown lists for all devices possible in
        mountwizzard. therefore we add the necessary entries to populate the list.

        :return: success for test
        """

        for name, selectorUI in self.selectorsDropDowns.items():
            selectorUI.clear()
            selectorUI.setView(PyQt5.QtWidgets.QListView())
            for headerEntry in self.fitsHeaderKeywords:
                selectorUI.addItem(headerEntry)

        return True

    @staticmethod
    def getNumberFiles(pathDir='', search=''):
        """
        getNumberFiles counts the number of files to be valid for the renaming.

        :param pathDir: path to root directory to be scanned
        :param search: search string
        :return: number of files found
        """

        if not pathDir:
            return 0
        if not os.path.isdir(pathDir):
            return 0
        if not search:
            return 0

        number = sum(1 for _ in Path(pathDir).glob(search))
        return number

    def convertHeaderEntry(self, entry='', fitsKey=''):
        """
        convertHeaderEntry takes the fitsHeader entry and reformat it to a reasonable
        string.

        :param entry:
        :param fitsKey:
        :return:
        """

        if not fitsKey:
            return ''
        if not entry:
            return ''

        if fitsKey == 'DATE-OBS':
            chunk = entry.replace(':', '-')
            chunk = chunk.replace('T', '-')
            chunk = chunk.split('.')[0]
        elif fitsKey == 'XBINNING':
            chunk = f'Bin{entry}'
        elif fitsKey == 'CCD-TEMP':
            chunk = f'Temp{entry:03.0f}'
        elif fitsKey == 'FRAME':
            chunk = f'{entry}'
        elif fitsKey == 'FILTER':
            chunk = f'{entry}'
        elif fitsKey == 'RenameText':
            chunk = self.ui.renameText.upper()
        else:
            chunk = ''

        return chunk

    def processSelectors(self, fitsHeader=None, selection=''):
        """
        processSelectors takes the selection for a fileName chunk and runs through the
        possible list of valid fits header keys. if there is more than one valid fitsKey,
        it automatically selects only the first on for conversion.

        :param fitsHeader:
        :param selection: str entry from the drop down selector
        :return: nameChunk: part of the entry
        """

        if fitsHeader is None:
            return ''
        if not selection:
            return ''

        nameChunk = ''
        fitsKeywords = self.fitsHeaderKeywords[selection]
        for fitsKey in fitsKeywords:
            if fitsKey not in fitsHeader:
                continue
            nameChunk = self.convertHeaderEntry(entry=fitsHeader[fitsKey],
                                                fitsKey=fitsKey)
            break
        return nameChunk

    def renameFile(self, fileName=''):
        """
        renameFile opens the given FITS file and retrieves it's header. if valid it
        runs through selectors of the drop down lists and checks all header keys to
        get the new filename build. afterwards it renames the given file.

        :param fileName: fits file to be renamed
        :return: success
        """

        if not fileName:
            return False

        with fits.open(name=fileName) as fd:
            fitsHeader = fd[0].header

            # object should bi in in any case. if not, it will be set
            if 'OBJECT' in fitsHeader:
                newFilename = fitsHeader['OBJECT'].lower()
            else:
                newFilename = 'unknown'

            for _, selector in self.selectorsDropDowns.items():
                selection = selector.currentText()
                chunk = self.processSelectors(fitsHeader=fitsHeader,
                                              selection=selection
                                              )
                if chunk:
                    newFilename += f'-{chunk}'

            newFilename += '.fits'

            dirName = os.path.dirname(fileName)
            newFilename = f'{dirName}/{newFilename}'
            os.rename(fileName, newFilename)

        return True

    def renameRunGUI(self):
        """
        renameRunGUI retrieves a full list of files to be renamed and renames
        them on by one.

        :return: True for test purpose
        """

        pathDir = self.ui.renameDir.text()
        includeSubdirs = self.ui.checkIncludeSubdirs.isChecked()

        if not os.path.isdir(pathDir):
            self.app.message.emit('No valid input directory given', 2)
            return False

        if includeSubdirs:
            search = '**/*.fit*'
        else:
            search = '*.fit*'

        numberFiles = self.getNumberFiles(pathDir, search=search)
        if not numberFiles:
            self.app.message.emit('No files to rename', 0)
            return False

        for i, fileName in enumerate(Path(pathDir).glob(search)):
            self.ui.renameProgress.setValue(int(100 * (i + 1) / numberFiles))
            PyQt5.QtWidgets.QApplication.processEvents()
            suc = self.renameFile(fileName=fileName)
            if not suc:
                self.app.message.emit(f'{fileName} could not be renamed', 2)

        self.app.message.emit(f'{numberFiles:d} images were renamed', 0)

        return True

    def chooseDir(self):
        """
        chooseDir selects the input directory and sets the default value for the
        output directory as well

        :return: True for test purpose
        """
        folder = self.ui.renameDir.text()
        pathDir, _, _ = self.openDir(self,
                                     'Choose Input Dir',
                                     folder,
                                     )
        if pathDir:
            self.ui.renameDir.setText(pathDir)
            self.ui.renameProgress.setValue(0)
        return True

    def moveNorth(self):
        """
        moveNorth slews the mount at speed.

        :return: success
        """

        self.app.mount.obsSite.moveNorth()
        self.changeStyleDynamic(self.ui.moveNorth, 'running', True)
        return True

    def moveEast(self):
        """
        moveEast slews the mount at speed.

        :return: success
        """

        self.app.mount.obsSite.moveEast()
        self.changeStyleDynamic(self.ui.moveEast, 'running', True)
        return True

    def moveSouth(self):
        """
        moveSouth slews the mount at speed.

        :return: success
        """

        self.app.mount.obsSite.moveSouth()
        self.changeStyleDynamic(self.ui.moveSouth, 'running', True)
        return True

    def moveWest(self):
        """
        moveWest slews the mount at speed.

        :return: success
        """

        self.app.mount.obsSite.moveWest()
        self.changeStyleDynamic(self.ui.moveWest, 'running', True)
        return True

    def moveNorthWest(self):
        """
        moveNorthWest slews the mount at speed.

        :return: success
        """

        self.app.mount.obsSite.moveWest()
        self.app.mount.obsSite.moveNorth()
        self.changeStyleDynamic(self.ui.moveNorthWest, 'running', True)
        return True

    def moveNorthEast(self):
        """
        moveNorthEast slews the mount at speed.

        :return: success
        """

        self.app.mount.obsSite.moveEast()
        self.app.mount.obsSite.moveNorth()
        self.changeStyleDynamic(self.ui.moveNorthEast, 'running', True)
        return True

    def moveSouthEast(self):
        """
        moveSouthEast slews the mount at speed.

        :return: success
        """

        self.app.mount.obsSite.moveEast()
        self.app.mount.obsSite.moveSouth()
        self.changeStyleDynamic(self.ui.moveSouthEast, 'running', True)
        return True

    def moveSouthWest(self):
        """
        moveSouthWest slews the mount at speed.

        :return: success
        """

        self.app.mount.obsSite.moveWest()
        self.app.mount.obsSite.moveSouth()
        self.changeStyleDynamic(self.ui.moveSouthWest, 'running', True)
        return True

    def stopMoveAll(self):
        """
        stopMoveAll stop the mount slew.

        :return: success
        """

        self.app.mount.obsSite.stopMoveAll()
        self.changeStyleDynamic(self.ui.moveNorth, 'running', False)
        self.changeStyleDynamic(self.ui.moveNorthEast, 'running', False)
        self.changeStyleDynamic(self.ui.moveEast, 'running', False)
        self.changeStyleDynamic(self.ui.moveSouthEast, 'running', False)
        self.changeStyleDynamic(self.ui.moveSouth, 'running', False)
        self.changeStyleDynamic(self.ui.moveSouthWest, 'running', False)
        self.changeStyleDynamic(self.ui.moveWest, 'running', False)
        self.changeStyleDynamic(self.ui.moveNorthWest, 'running', False)
        return True

    def setSlewSpeed(self):
        """

        :return: success
        """

        for key, ui, func in zip(self.slewSpeeds.keys(),
                                 self.slewSpeeds.values(),
                                 self.slewSpeedFuncs.values()):
            if ui != self.sender():
                self.changeStyleDynamic(ui, 'running', False)
                continue
            self.changeStyleDynamic(ui, 'running', True)
            self.slewSpeedSelected = key
            func()

        return True
