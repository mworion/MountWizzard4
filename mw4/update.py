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
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import sys
import logging
import subprocess
import platform
import time

# external packages

# local import
from base.loggerMW import setupLogging

setupLogging()
log = logging.getLogger()


class Update:
    log = logging.getLogger(__name__)

    def __init__(self, runnable=None, writer=None):
        self.writer = writer
        self.runnable = runnable

    @staticmethod
    def formatPIP(line=''):
        """
        formatPIP shortens the stdout line for presenting it to the user. as the
        lines are really long, mw4 concentrates on package names and action.

        :param line:
        :return: formatted line
        """
        if line.startswith(' '):
            return ''

        elif line.startswith('Requirement'):
            val = line.split(':')
            prefix = val[0]
            packageName = val[1].split('<')[0].split('>')[0].split('=')[0].split(' ')[1]
            line = f'{prefix} : {packageName}'

        elif line.startswith('Collecting'):
            line = line.split('<')[0].split('>')[0].split('=')[0]

        elif line.startswith('Installing') or line.startswith('Building'):
            line = line.split(':')[0]

        else:
            line = line.split('\n')[0]

        return line

    def runInstall(self, versionPackage=''):
        """
        :param versionPackage:   package version to install
        :return: success
        """
        runnable = ['pip',
                    'install',
                    f'mountwizzard4=={versionPackage}',
                    '--disable-pip-version-check',
                    ]

        try:
            process = subprocess.Popen(args=runnable,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       text=True,
                                       )
            for stdout_line in iter(process.stdout.readline, ""):
                line = self.formatPIP(line=stdout_line)
                if line:
                    self.writer(line, 0)

            output = process.communicate(timeout=60)[0]

        except subprocess.TimeoutExpired as e:
            self.log.error(e)
            return False

        except Exception as e:
            self.log.error(f'Error: {e} happened')
            return False

        else:
            retCode = str(process.returncode)
            self.log.debug(f'pip install: [{retCode}] [{output}]')

        success = (process.returncode == 0)
        return success

    def restart(self, text):
        """
        :param text:
        :return:
        """
        runDir = os.path.dirname(self.runnable)
        runScript = os.path.abspath(runDir + '/loader.py')
        pythonPath = os.path.abspath(sys.executable)

        if platform.system() == 'Windows':
            runScript = "\"" + runScript + "\""
            pythonRuntime = "\"" + pythonPath + "\""
        else:
            pythonRuntime = pythonPath

        if platform.system() == 'Windows':
            text = "\"" + text + "\""

        os.execl(pythonPath, pythonRuntime, runScript, text)
        return True


class UpdateGUI:
    log = logging.getLogger(__name__)

    def __init__(self, runnable=None, version=None, x=0, y=0):
        self.version = version

        from PyQt5.QtTest import QTest
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QIcon, QPixmap
        from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout
        from PyQt5.QtWidgets import QHBoxLayout, QWidget, QTextBrowser, QLabel
        import resource.resources as res
        res.qInitResources()
        from gui.utilities.stylesQtCss import Styles

        self.test = QTest
        self.update = Update(runnable=runnable, writer=self.writeText)

        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon(':/icon/mw4.ico'))

        self.mColor = [Styles.COLOR_ASTRO,
                       Styles.COLOR_WHITE,
                       Styles.COLOR_YELLOW,
                       Styles.COLOR_RED,
                       ]
        isMac = platform.system() == 'Darwin'
        addStyle = Styles.MAC_STYLE if isMac else Styles.NON_MAC_STYLE
        self.style = addStyle + Styles.BASIC_STYLE

        self.window = QWidget()
        self.window.setWindowTitle('MountWizzard4 Updater')
        self.window.resize(500, 300)
        self.window.move(x, y)
        self.window.setStyleSheet(self.style)

        self.cancelButt = QPushButton('Cancel Update')
        self.cancelButt.setFixedHeight(25)
        self.updateButt = QPushButton('Start Update')
        self.updateButt.setFixedHeight(25)
        self.textBrow = QTextBrowser()
        self.textBrow.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.updateButt.clicked.connect(self.runUpdate)
        self.cancelButt.clicked.connect(self.runCancel)

        layoutMain = QVBoxLayout()
        layoutHeader = QHBoxLayout()
        layoutButtons = QHBoxLayout()
        header = QLabel()
        iconLabel = QLabel()
        pixmap = QPixmap(':icon/mw4.png').scaled(32, 32)
        iconLabel.setPixmap(pixmap)
        layoutHeader.addWidget(iconLabel)
        header.setText(f'Update to version: [{self.version}]')
        header.setStyleSheet('font-size: 18pt;')
        layoutHeader.addWidget(header)
        question = QLabel()
        pixmap = QPixmap(':/icon/question.svg').scaled(32, 32)
        question.setPixmap(pixmap)
        question.setAlignment(Qt.AlignRight)
        layoutHeader.addWidget(question)
        layoutButtons.addWidget(self.cancelButt)
        layoutButtons.addWidget(self.updateButt)
        layoutMain.addLayout(layoutHeader)
        layoutMain.addWidget(self.textBrow)
        layoutMain.addLayout(layoutButtons)
        self.window.setLayout(layoutMain)
        self.window.show()

    def run(self):
        sys.exit(self.app.exec_())

    def writeText(self, text, color):
        """
        :param text:
        :param color:
        :return:
        """
        from PyQt5.QtGui import QTextCursor
        from PyQt5.QtWidgets import QApplication

        self.textBrow.setTextColor(self.mColor[color])
        self.textBrow.insertPlainText(text + '\n')
        self.textBrow.moveCursor(QTextCursor.End)
        self.log.ui(f'Updater window: [{text}]')
        QApplication.processEvents()
        return True

    def runCancel(self):
        """
        :return:
        """
        self.cancelButt.setEnabled(False)
        self.updateButt.setEnabled(False)
        text = 'Update cancelled'
        self.writeText(text, 2)
        self.writeText('Restarting MountWizzard4...', 1)
        self.writeText('...this takes some seconds...', 1)
        self.test.qWait(3000)
        self.update.restart(text)
        return True

    def runUpdate(self):
        """
        :return:
        """
        self.cancelButt.setEnabled(False)
        self.updateButt.setEnabled(False)
        self.writeText(f'Installing now version {self.version}', 1)
        self.test.qWait(1000)
        suc = self.update.runInstall(self.version)
        if suc:
            text = f'Successfully installed {self.version}'
            self.writeText(text, 1)
        else:
            text = f'Error installing {self.version}'
            self.writeText(text, 2)

        self.writeText(f'Restarting MountWizzard4...', 1)
        self.writeText('...this takes some seconds...', 1)
        self.test.qWait(3000)
        self.update.restart(text)
        return True


class UpdateCLI:
    log = logging.getLogger(__name__)

    def __init__(self, runnable=None, version=None):
        self.version = version
        self.update = Update(runnable=runnable, writer=self.writeText)

        self.writeText(f'Installing now version {self.version}', 1)
        time.sleep(1)
        suc = self.update.runInstall(self.version)
        if suc:
            text = f'Successfully installed {self.version}'
            self.writeText(text, 1)
        else:
            text = f'Error installing {self.version}'
            self.writeText(text, 2)

        self.writeText(f'Restarting MountWizzard4...', 1)
        self.writeText('...this takes some seconds...', 1)
        self.update.restart(text)

    def writeText(self, text, color):
        """
        :return:
        """
        sys.stdout.write(text + '\n')
        self.log.ui(f'Updater terminal: [{text}]')
        return True


def main():
    """
    :return: nothing
    """
    runnable = sys.argv[0]
    version = sys.argv[1]
    x = int(sys.argv[2]) + 150
    y = int(sys.argv[3]) + 150
    simpleGui = sys.argv[4] == 'CLI'

    log.header('-' * 100)
    log.header(f'Running updater')
    if simpleGui:
        log.header(f'Simple updater in CLI mode')
    else:
        log.header(f'Comfort updater in GUI mode')

    log.header('-' * 100)

    if simpleGui:
        UpdateCLI(runnable=runnable, version=version)
    else:
        u = UpdateGUI(runnable=runnable, version=version, x=x, y=y)
        u.run()


if __name__ == "__main__":
    main()
