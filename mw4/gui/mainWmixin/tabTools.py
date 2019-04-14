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
from shutil import copyfile
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
        self.ui.renameInputSelect.clicked.connect(self.chooseInputDir)
        self.ui.renameOutputSelect.clicked.connect(self.chooseOutputDir)
        # self.ui.renameCanel.clicked.connect(self.loadProfile)

    def initConfig(self):
        config = self.app.config['mainW']
        self.ui.renameInput.setText(config.get('renameInput', ''))
        self.ui.renameOutput.setText(config.get('renameOutput', ''))
        self.ui.renameProgress.setValue(0)
        return True

    def storeConfig(self):
        config = self.app.config['mainW']
        config['renameInput'] = self.ui.renameInput.text()
        config['renameOutput'] = self.ui.renameOutput.text()
        return True

    def setupIcons(self):
        """
        setupIcons add icon from standard library to certain buttons for improving the
        gui of the app.

        :return:    True if success for test
        """

        self.wIcon(self.ui.renameStart, PyQt5.QtWidgets.QStyle.SP_DialogApplyButton)
        self.wIcon(self.ui.renameCancel, PyQt5.QtWidgets.QStyle.SP_DialogCancelButton)

        return True

    def clearGUI(self):
        """
        clearGUI rewrites the gui in case of a special event needed for clearing up

        :return: success for test
        """
        return True

    def getNumberFiles(self, path=''):
        """

        :param path:
        :return: number
        """
        number = 0
        for filename in glob.iglob(path + '**/*.fit*', recursive=True):
            number += 1
        return number

    def renameRun(self, inputPath='', outputPath=''):
        """

        :param inputPath:
        :param outputPath:
        :return:
        """

        numberFiles = self.getNumberFiles(inputPath)
        self.app.message.emit(f'There will be {numberFiles:4d} images renamed', 0)

        count = 0
        for filename in glob.iglob(inputPath + '**/*.fit*', recursive=True):
            count += 1
            self.ui.renameProgress.setValue(int(100 * count / numberFiles))
            PyQt5.QtWidgets.QApplication.processEvents()
            with fits.open(name=filename) as fd:
                if 'FRAME' not in fd[0].header:
                    continue
                if 'FILTER' not in fd[0].header:
                    continue
                if 'XBINNING' not in fd[0].header:
                    continue
                if 'DATE-OBS' not in fd[0].header:
                    continue

                newFilename = outputPath + '/{0}{1:}_{2}_BIN_{3:01d}_{4}' \
                    .format('M15_',
                            fd[0].header['FRAME'],
                            fd[0].header['FILTER'],
                            int(fd[0].header['XBINNING']),
                            fd[0].header['DATE-OBS'],
                            )
                newFilename = newFilename.replace(':', '_')
                newFilename = newFilename.replace('.', '_')
                newFilename = newFilename.replace('-', '_')
                newFilename = newFilename.replace('T', '_')
                newFilename += '.fits'
                self.ui.renameText.insertPlainText(newFilename + '\n')
            copyfile(filename, newFilename)
        return True

    def renameRunGUI(self):
        """

        :return: True for test purpose
        """

        inputPath = self.ui.renameInput.text()
        outputPath = self.ui.renameOutput.text()
        if not os.path.isdir(inputPath):
            self.app.message.emit('No valid input directory given', 2)
            return False
        if not os.path.isdir(outputPath):
            os.mkdir(outputPath, 0o777)

        self.renameRun(inputPath=inputPath, outputPath=outputPath)
        return True

    def chooseInputDir(self):
        """
        chooseInputDir selects the input directory and sets the default value for the
        output directory as well

        :return: True for test purpose
        """
        folder = self.ui.renameInput.text()
        inputPath, _, _ = self.openDir(self,
                                       'Choose Input Dir',
                                       folder,
                                       )
        if inputPath:
            self.ui.renameInput.setText(inputPath)
            self.ui.renameOutput.setText(inputPath + '/output')
        return True

    def chooseOutputDir(self):
        """
        chooseOutputDir selects the output directory ‚

        :return: True for test purpose
        """
        folder = self.ui.renameInput.text()
        outputPath, _, _ = self.openDir(self,
                                        'Choose Output Dir',
                                        folder,
                                        )
        if outputPath:
            self.ui.renameOutput.setText(outputPath)
        return True
