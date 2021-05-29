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

# external packages
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QTextCursor, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QTextBrowser, QLabel

# local import
from base.loggerMW import setupLogging
from gui.utilities.stylesQtCss import Styles
import resource.resources as res
res.qInitResources()

setupLogging()
log = logging.getLogger()

mColor = [Styles.COLOR_ASTRO,
          Styles.COLOR_WHITE,
          Styles.COLOR_YELLOW,
          Styles.COLOR_RED,
          ]


def writeText(textBrow, t, color):
    """
    :param textBrow:
    :param t:
    :param color:
    :return:
    """
    textBrow.setTextColor(mColor[color])
    textBrow.insertPlainText(t + '\n')
    textBrow.moveCursor(QTextCursor.End)
    log.ui(f'Updater window: [{t}]')
    QApplication.processEvents()
    return True


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


def runInstall(textBrow, versionPackage=''):
    """
    :param textBrow:
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
            line = formatPIP(line=stdout_line)
            if line:
                writeText(textBrow, line, 0)

        output = process.communicate(timeout=60)[0]

    except subprocess.TimeoutExpired as e:
        log.error(e)
        return False

    except Exception as e:
        log.error(f'Error: {e} happened')
        return False

    else:
        retCode = str(process.returncode)
        log.debug(f'pip install: [{retCode}] [{output}]')

    success = (process.returncode == 0)
    return success


def runCancel(textBrow):
    """
    :return:
    """
    writeText(textBrow, 'Update cancelled', 2)
    writeText(textBrow, 'Restarting MountWizzard4...', 1)
    QTest.qWait(3000)

    runDir = os.path.dirname(sys.argv[0])
    runFull = runDir + '/loader.py'
    python = sys.executable
    os.execl(python, python, runFull)
    return True


def runUpdate(textBrow, version):
    """
    :return:
    """
    writeText(textBrow, f'Installing now version {version}', 1)

    suc = runInstall(textBrow, version)
    if suc:
        writeText(textBrow, f'Successfully installed {version}', 1)
    else:
        writeText(textBrow, 'Error installing {version}', 2)

    writeText(textBrow, f'Restarting MountWizzard4...', 1)
    QTest.qWait(3000)

    runDir = os.path.dirname(sys.argv[0])
    runFull = runDir + '/loader.py'
    python = sys.executable
    os.execl(python, python, runFull)
    return True


def main():
    """
    :return: nothing
    """
    version = sys.argv[1]
    log.header('-' * 100)
    log.header(f'Running updater')
    log.header('-' * 100)

    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/icon/mw4.ico'))
    window = QWidget()
    window.setWindowTitle('MountWizzard4 Updater')
    window.resize(800, 600)
    window.move(int(sys.argv[2]), int(sys.argv[3]))

    if platform.system() == 'Darwin':
        style = Styles.MAC_STYLE + Styles.BASIC_STYLE
    else:
        style = Styles.NON_MAC_STYLE + Styles.BASIC_STYLE
    window.setStyleSheet(style)

    cancel = QPushButton('Cancel Update')
    cancel.setFixedHeight(25)
    update = QPushButton('Start Update')
    update.setFixedHeight(25)
    textBrow = QTextBrowser()

    update.clicked.connect(lambda: runUpdate(textBrow, version))
    cancel.clicked.connect(lambda: runCancel(textBrow))

    layoutMain = QVBoxLayout()
    layoutHeader = QHBoxLayout()
    layoutButtons = QHBoxLayout()

    header = QLabel()
    iconLabel = QLabel()
    pixmap = QPixmap(':icon/mw4.png').scaled(128, 128)
    iconLabel.setPixmap(pixmap)
    layoutHeader.addWidget(iconLabel)

    header.setText(f'Update to version: [{version}]')
    header.setStyleSheet('font-size: 28pt;')
    layoutHeader.addWidget(header)

    question = QLabel()
    pixmap = QPixmap(':/icon/question.svg').scaled(128, 128)
    question.setPixmap(pixmap)
    question.setAlignment(Qt.AlignRight)
    layoutHeader.addWidget(question)

    layoutButtons.addWidget(cancel)
    layoutButtons.addWidget(update)
    layoutMain.addLayout(layoutHeader)
    layoutMain.addWidget(textBrow)
    layoutMain.addLayout(layoutButtons)
    window.setLayout(layoutMain)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
