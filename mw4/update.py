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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import sys
import logging
import subprocess
import platform

# external packages

# local import
from base.loggerMW import setupLogging

setupLogging(redirect=False)
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
            line = line.split('<')[0].split('>')[0].split('=')[0].rstrip()

        elif line.startswith('Installing') or line.startswith('Building'):
            line = line.split(':')[0].rstrip()

        else:
            line = line.split('\n')[0].rstrip()

        return line

    def isVenv(self):
        """
        detects if the actual package is running in a virtual environment. this
        should be the case in any situation as mw4 should be installed in a venv.

        :return: status
        """
        hasReal = hasattr(sys, 'real_prefix')
        hasBase = hasattr(sys, 'base_prefix')

        status = hasReal or hasBase and sys.base_prefix != sys.prefix
        if hasReal:
            self.log.debug(f'Real prefix: [{sys.real_prefix}]')
        if hasBase:
            self.log.debug(f'Base prefix: [{sys.base_prefix}]')
        self.log.debug(f'PATH:        [{os.environ.get("PATH", "")}]')
        self.log.debug(f'VENV path:   [{os.environ.get("VIRTUAL_ENV", "")}]')
        self.log.debug(f'VENV status: [{status}]')
        return status

    def runInstall(self, versionPackage=''):
        """
        :param versionPackage:   package version to install
        :return: success
        """
        if not self.isVenv():
            self.writer('Updater not running in an virtual environment', 2)
            return False

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

    def __init__(self, runnable=None, version=None, x=0, y=0, colorSet=0):
        self.version = version

        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter
        from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout
        from PyQt6.QtWidgets import QHBoxLayout, QWidget, QTextBrowser, QLabel
        import resource.resources as res
        res.qInitResources()
        from gui.utilities.stylesQtCss import Styles

        self.update = Update(runnable=runnable, writer=self.writeText)

        QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
        self.app = QApplication(sys.argv)
        self.style = Styles()
        self.style.colorSet = colorSet
        self.app.setWindowIcon(QIcon(':/icon/mw4.ico'))
        self.mColor = [QColor(self.style.M_BLUE),
                       QColor(self.style.M_WHITE),
                       QColor(self.style.M_YELLOW),
                       QColor(self.style.M_RED),
                       ]

        self.window = QWidget()
        self.window.setWindowTitle('MountWizzard4 Updater')
        self.window.resize(500, 300)
        self.window.move(x, y)
        self.window.setStyleSheet(self.style.mw4Style)

        self.cancelButt = QPushButton('Cancel Update')
        self.cancelButt.setFixedHeight(25)
        self.updateButt = QPushButton('Start Update')
        self.updateButt.setFixedHeight(25)
        self.textBrow = QTextBrowser()
        self.textBrow.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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

        img = QPixmap(':/icon/question.svg')
        qp = QPainter(img)
        qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        qp.fillRect(img.rect(), QColor(self.style.M_BLUE))
        qp.end()
        pixmap = QPixmap(img).scaled(32, 32)
        question.setPixmap(pixmap)
        question.setAlignment(Qt.AlignmentFlag.AlignRight)
        layoutHeader.addWidget(question)
        layoutButtons.addWidget(self.cancelButt)
        layoutButtons.addWidget(self.updateButt)
        layoutMain.addLayout(layoutHeader)
        layoutMain.addWidget(self.textBrow)
        layoutMain.addLayout(layoutButtons)
        self.window.setLayout(layoutMain)
        self.window.show()

    def run(self):
        sys.exit(self.app.exec())

    def writeText(self, text, color):
        """
        :param text:
        :param color:
        :return:
        """
        from PyQt6.QtGui import QTextCursor
        from PyQt6.QtWidgets import QApplication

        self.textBrow.setTextColor(self.mColor[color])
        self.textBrow.insertPlainText(text + '\n')
        self.textBrow.moveCursor(QTextCursor.MoveOperation.End)
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
        self.update.restart(text)
        return True

    def runUpdate(self):
        """
        :return:
        """
        self.cancelButt.setEnabled(False)
        self.updateButt.setEnabled(False)
        self.writeText(f'Installing now version {self.version}', 1)
        suc = self.update.runInstall(self.version)
        if suc:
            text = f'Successfully installed {self.version}'
            self.writeText(text, 1)
        else:
            text = f'Error installing {self.version}'
            self.writeText(text, 2)

        self.writeText('Restarting MountWizzard4...', 1)
        self.writeText('...this takes some seconds...', 1)
        self.update.restart(text)
        return True


class UpdateCLI:
    log = logging.getLogger(__name__)

    def __init__(self, runnable=None, version=None):
        self.version = version
        self.update = Update(runnable=runnable, writer=self.writeText)

        self.writeText(f'Installing now version {self.version}', 1)
        suc = self.update.runInstall(self.version)
        if suc:
            text = f'Successfully installed {self.version}'
            self.writeText(text, 1)
        else:
            text = f'Error installing {self.version}'
            self.writeText(text, 2)

        self.writeText('Restarting MountWizzard4...', 1)
        self.writeText('...this takes some seconds...', 1)
        self.update.restart(text)

    def writeText(self, text, color):
        """
        :param text:
        :param color:
        :return:
        """
        print(text + '\n')
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
    colorSet = int(sys.argv[5])

    log.header('-' * 100)
    log.header('Running updater')
    if simpleGui:
        log.header('Simple updater in CLI mode')
    else:
        log.header('Comfort updater in GUI mode')

    log.header('-' * 100)

    if simpleGui:
        UpdateCLI(runnable=runnable, version=version)
    else:
        u = UpdateGUI(runnable=runnable, version=version, x=x, y=y,
                      colorSet=colorSet)
        u.run()


if __name__ == "__main__":
    main()
