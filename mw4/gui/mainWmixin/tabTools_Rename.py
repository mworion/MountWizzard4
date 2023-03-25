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
import os
from pathlib import Path

# external packages
from PyQt5.QtWidgets import QListView, QApplication
from astropy.io import fits

# local import


class Rename:
    """
    """

    def __init__(self):
        self.selectorsDropDowns = {'rename1': self.ui.rename1,
                                   'rename2': self.ui.rename2,
                                   'rename3': self.ui.rename3,
                                   'rename4': self.ui.rename4,
                                   'rename5': self.ui.rename5,
                                   'rename6': self.ui.rename6,
                                   }
        self.fitsHeaderKeywords = {'None': [''],
                                   'Datetime': ['DATE-OBS'],
                                   'Frame': ['FRAME', 'IMAGETYP'],
                                   'Filter': ['FILTER'],
                                   'Binning': ['XBINNING'],
                                   'Exp Time': ['EXPTIME'],
                                   'CCD Temp': ['CCD-TEMP'],
                                   }
        self.setupGuiTools()
        self.ui.renameStart.clicked.connect(self.renameRunGUI)
        self.ui.renameInputSelect.clicked.connect(self.chooseDir)

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
        self.ui.newObjectName.setText(config.get('newObjectName', ''))
        self.ui.includeSubdirs.setChecked(config.get('includeSubdirs', False))
        for name, ui in self.selectorsDropDowns.items():
            ui.setCurrentIndex(config.get(name, 0))

        self.ui.renameProgress.setValue(0)
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
        config['newObjectName'] = self.ui.newObjectName.text()
        config['includeSubdirs'] = self.ui.includeSubdirs.isChecked()
        for name, ui in self.selectorsDropDowns.items():
            config[name] = ui.currentIndex()

        return True

    def setupGuiTools(self):
        """
        :return: success for test
        """
        for name, selectorUI in self.selectorsDropDowns.items():
            selectorUI.clear()
            selectorUI.setView(QListView())
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

    @staticmethod
    def convertHeaderEntry(entry='', fitsKey=''):
        """
        convertHeaderEntry takes the fitsHeader entry and reformat it to a
        reasonable string.

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
            chunk = chunk.replace('T', '_')
            chunk = chunk.split('.')[0]
        elif fitsKey == 'XBINNING':
            chunk = f'Bin{entry:1.0f}'
        elif fitsKey == 'CCD-TEMP':
            chunk = f'Temp{entry:03.0f}'
        elif fitsKey == 'FRAME':
            chunk = f'{entry}'
        elif fitsKey == 'FILTER':
            chunk = f'{entry}'
        elif fitsKey == 'EXPTIME':
            chunk = f'Exp{entry:1.0f}s'
        else:
            chunk = ''

        return chunk

    def processSelectors(self, fitsHeader=None, selection=''):
        """
        processSelectors takes the selection for a fileName chunk and runs through the
        possible list of valid fits header keys. if there is more than one valid fitsKey,
        it automatically selects only the first on for conversion.

        :param fitsHeader:
        :param selection: str entry from the drop-down selector
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
        renameFile opens the given FITS file and retrieves its header. if valid it
        runs through selectors of the drop-down lists and checks all header keys to
        get the new filename build. afterwards it renames the given file.

        :param fileName: fits file to be renamed
        :return: success
        """
        if not fileName:
            return False
        if not os.path.isfile(fileName):
            return False

        fileName = os.path.normpath(fileName)
        with fits.open(name=fileName) as fd:
            fitsHeader = fd[0].header

            # object should be in lower case. if not, it will be set
            newObjectName = self.ui.newObjectName.text().upper()
            if newObjectName:
                newFilename = newObjectName

            else:
                if 'OBJECT' in fitsHeader:
                    newFilename = fitsHeader['OBJECT'].upper()
                else:
                    newFilename = 'UNKNOWN'

            for _, selector in self.selectorsDropDowns.items():
                selection = selector.currentText()
                chunk = self.processSelectors(fitsHeader=fitsHeader,
                                              selection=selection
                                              )
                if chunk:
                    newFilename += f'_{chunk}'

            newFilename += '.fits'
            dirName = os.path.dirname(fileName)
            newFilename = os.path.normpath(f'{dirName}/{newFilename}')
            os.rename(fileName, newFilename)

        return True

    def renameRunGUI(self):
        """
        renameRunGUI retrieves a full list of files to be renamed and renames
        them on by one.

        :return: True for test purpose
        """
        pathDir = self.ui.renameDir.text()
        includeSubdirs = self.ui.includeSubdirs.isChecked()
        if not os.path.isdir(pathDir):
            self.msg.emit(2, 'Tools', 'Rename error',
                          'No valid input directory given')
            return False

        if includeSubdirs:
            search = '**/*.fit*'
        else:
            search = '*.fit*'

        numberFiles = self.getNumberFiles(pathDir, search=search)
        if not numberFiles:
            self.msg.emit(2, 'Tools', 'Rename error',
                          'No files to rename')
            return False

        for i, fileName in enumerate(Path(pathDir).glob(search)):
            self.ui.renameProgress.setValue(int(100 * (i + 1) / numberFiles))
            QApplication.processEvents()
            suc = self.renameFile(fileName=fileName)
            if not suc:
                self.msg.emit(2, 'Tools', 'Rename error',
                              f'{fileName} could not be renamed')

        self.msg.emit(0, 'Tools', 'Rename',
                      f'{numberFiles:d} images were renamed')

        return True

    def chooseDir(self):
        """
        chooseDir selects the input directory and sets the default value for the
        output directory as well

        :return: True for test purpose
        """
        folder = self.ui.renameDir.text()
        pathDir, _, _ = self.openDir(self, 'Choose Input Dir', folder,)
        if pathDir:
            self.ui.renameDir.setText(pathDir)
            self.ui.renameProgress.setValue(0)
        return True
