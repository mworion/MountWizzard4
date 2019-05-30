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
import os
import glob
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
        self.ui.renameStart.clicked.connect(self.renameRunGUI)
        self.ui.renameInputSelect.clicked.connect(self.chooseDir)

        self.selectorsDropDowns = {'rename1': self.ui.rename1,
                                   'rename2': self.ui.rename2,
                                   'rename3': self.ui.rename3,
                                   'rename4': self.ui.rename4,
                                   'rename5': self.ui.rename5,
                                   }
        self.headerKeywords = {'None': [''],
                               'Frame': ['FRAME'],
                               'Filter': ['FILTER'],
                               'Binning': ['XBINNING'],
                               'Datetime': ['DATE-OBS'],
                               'CCD Temp': ['CCD-TEMP'],
                               'Exp Time': ['EXPTIME'],
                                }

        self.setupSelectorGui()

    def initConfig(self):
        config = self.app.config['mainW']
        defaultDir = self.app.mwGlob['imageDir']
        self.ui.renameDir.setText(config.get('renameDir', defaultDir))
        self.ui.checkIncludeSubdirs.setChecked(config.get('checkIncludeSubdirs', False))
        for name, ui in self.selectorsDropDowns.items():
            ui.setCurrentIndex(config.get(name, 0))

        self.ui.renameProgress.setValue(0)
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['renameDir'] = self.ui.renameDir.text()
        config['checkIncludeSubdirs'] = self.ui.checkIncludeSubdirs.isChecked()
        for name, ui in self.selectorsDropDowns.items():
            config[name] = ui.currentIndex()

        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """

        self.wIcon(self.ui.renameStart, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)

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
            for headerEntry in self.headerKeywords:
                selectorUI.addItem(headerEntry)

    def getNumberFiles(self, path='', subdirs=False):
        """

        :param path:
        :param subdirs:
        :return: number
        """
        number = 0
        for filename in glob.iglob(path + '**/*.fit*', recursive=subdirs):
            number += 1
        return number

    def convertHeaderEntry(self, entry='', keyword=''):
        """

        :param entry:
        :param keyword:
        :return:
        """

        if not keyword:
            return ''
        if not entry:
            return ''

        if keyword == 'DATE-OBS':
            chunk = entry.replace(':', '-')
            chunk = chunk.replace('T', '-')
            chunk = chunk.replace('.', '-')
        elif keyword == 'XBINNING':
            chunk = f'Bin{entry}'
        else:
            chunk = ''

        return chunk

    def processSelectors(self, header=None, index=''):
        """

        :param header:
        :param index:
        :return: nameChunk: part of the entry
        """

        if header is None:
            return ''
        if not index:
            return ''

        nameChunk = ''
        keywords = self.headerKeywords[index]
        for keyword in keywords:
            if keyword not in header:
                continue
            nameChunk = self.convertHeaderEntry(entry=header[keyword],
                                                keyword=keyword)
            break

        return nameChunk

    def renameFile(self, fileName=''):
        """

        :param fileName:
        :return:
        """

        if not fileName:
            return False

        with fits.open(name=fileName) as fd:
            header = fd[0].header

            if 'OBJECT' in header:
                newFilename = header['OBJECT'].capitalize()
            else:
                newFilename = 'UNKNOWN'

            for _, selector in self.selectorsDropDowns.items():
                index = selector.currentText()
                chunk = self.processSelectors(header=header,
                                              index=index
                                              )
                if chunk:
                    newFilename += f'-{chunk}'

            newFilename += '.fits'
            print(fileName, newFilename)
            # os.rename(fileName, newFilename)
        return True

    def renameRunGUI(self):
        """

        :return: True for test purpose
        """

        inputPath = self.ui.renameDir.text()
        includeSubdirs = self.ui.checkIncludeSubdirs.isChecked()

        if not os.path.isdir(inputPath):
            self.app.message.emit('No valid input directory given', 2)
            return False

        numberFiles = self.getNumberFiles(inputPath)
        self.app.message.emit(f'There will be {numberFiles:4d} images renamed', 0)

        for i, fileName in enumerate(glob.iglob(inputPath + '**/*.fit*',
                                                recursive=includeSubdirs)):
            self.ui.renameProgress.setValue(int(100 * (i + 1) / numberFiles))
            PyQt5.QtWidgets.QApplication.processEvents()

            self.renameFile(fileName=fileName)

        return True

    def chooseDir(self):
        """
        chooseDir selects the input directory and sets the default value for the
        output directory as well

        :return: True for test purpose
        """
        folder = self.ui.renameDir.text()
        inputPath, _, _ = self.openDir(self,
                                       'Choose Input Dir',
                                       folder,
                                       )
        if inputPath:
            self.ui.renameDir.setText(inputPath)
            self.ui.renameProgress.setValue(0)
        return True
