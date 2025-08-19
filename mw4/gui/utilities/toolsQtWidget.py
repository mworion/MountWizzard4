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
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import time
import logging
import datetime
from dateutil.tz import tzlocal
from pathlib import Path

# external packages
from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QWidget, QFileDialog, QMessageBox
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtGui import QPalette, QIcon, QPixmap, QColor, QPainter, QImage
from PySide6.QtGui import QPainterPath, QTransform, QGuiApplication
from PySide6.QtCore import QDir, QObject, Signal
from PySide6.QtCore import Qt, QSize, QEvent
import numpy as np
from qimage2ndarray import rgb_view, array2qimage

# local imports
from gui.styles.styles import Styles
from mountcontrol.convert import formatHstrToText, formatDstrToText


def sleepAndEvents(value: int) -> None:
    """ """
    for _ in range(value):
        time.sleep(0.001)
        QCoreApplication.processEvents()


def changeStyleDynamic(widget: QWidget, widgetProperty: str, value: str) -> None:
    """ """
    if widget.property(widgetProperty) == value:
        return

    widget.style().unpolish(widget)
    widget.setProperty(widgetProperty, value)
    widget.style().polish(widget)


def findIndexValue(ui, searchString, relaxed=False):
    """ """
    for index in range(ui.model().rowCount()):
        modelIndex = ui.model().index(index, 0)
        indexValue = ui.model().data(modelIndex)

        if not indexValue:
            continue
        if relaxed:
            if searchString in indexValue:
                return index
        else:
            if indexValue.startswith(searchString):
                return index
    return 0


def guiSetStyle(ui, pStyle="", value=None, pVals=None):
    """ """
    if pVals is None:
        pVals = ["", "", ""]
    if not pStyle:
        return
    if value is None:
        pVal = pVals[0]
    elif value:
        pVal = pVals[1]
    else:
        pVal = pVals[2]

    changeStyleDynamic(ui, pStyle, pVal)


def guiSetText(ui, formatElement, value=None):
    """ """
    if not ui:
        return
    if not formatElement:
        return
    if value is None:
        text = "-"
    elif isinstance(value, (list, np.ndarray)) and len(value) == 0:
        text = "-"
    elif formatElement.startswith("HSTR"):
        text = formatHstrToText(value)
    elif formatElement.startswith("DSTR"):
        text = formatDstrToText(value)
    elif formatElement.startswith("D"):
        formatStr = "{0:" + formatElement.lstrip("D") + "}"
        text = formatStr.format(value.degrees)
    elif formatElement.startswith("H"):
        formatStr = "{0:" + formatElement.lstrip("H") + "}"
        text = formatStr.format(value.hours)
    elif value == "E":
        text = "EAST"
    elif value == "W":
        text = "WEST"
    elif isinstance(value, bool):
        if value:
            text = "ON"
        else:
            text = "OFF"
    else:
        formatStr = "{0:" + formatElement + "}"
        text = formatStr.format(value)

    ui.setText(text)


def clickable(widget: QWidget) -> Signal:
    """ """

    class MouseClickEventFilter(QObject):
        clicked = Signal(object)

        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.MouseButtonRelease:
                if obj.rect().contains(event.pos()):
                    self.clicked.emit(widget)
                return True
            else:
                return False

    clickEventFilter = MouseClickEventFilter(widget)
    widget.installEventFilter(clickEventFilter)
    return clickEventFilter.clicked


class MWidget(QWidget, Styles):
    """ """

    log = logging.getLogger("MW4")

    def __init__(self):
        super().__init__()

        self.palette = QPalette()
        self.initUI()
        self.screenSizeX = QGuiApplication.primaryScreen().geometry().width()
        self.screenSizeY = QGuiApplication.primaryScreen().geometry().height()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        newFlag = Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowSystemMenuHint
        newFlag = (
            newFlag
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
        )
        self.setWindowFlags(self.windowFlags() | newFlag)
        self.setWindowIcon(QIcon(":/icon/mw4.png"))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.app = None

    @staticmethod
    def saveWindowAsPNG(window):
        """ """
        name = window.windowTitle().replace(" ", "_")
        timeTrigger = datetime.datetime.now(datetime.timezone.utc)
        timeTag = timeTrigger.strftime("%Y-%m-%d-%H-%M-%S")
        path = window.app.mwGlob["logDir"]
        fullFileName = f"{path}/{timeTag}-{name}.png"
        window.log.info(f"Screenshot: [{fullFileName}]")
        window.grab().save(fullFileName)

    def saveAllWindowsAsPNG(self, window):
        """ """
        windows = window.app.mainW.externalWindows.uiWindows
        self.saveWindowAsPNG(window)
        for window in windows:
            obj = windows[window]["classObj"]
            if obj:
                self.saveWindowAsPNG(obj)

    def keyPressEvent(self, keyEvent):
        """
        Pressing F5 makes a screen copy of the actual window
        Pressing F6 makes a screen copy of all open windows
        """
        if keyEvent.key() == 16777268:
            self.saveWindowAsPNG(self)
            return
        elif keyEvent.key() == 16777269:
            self.saveAllWindowsAsPNG(self)
            return
        super().keyPressEvent(keyEvent)

    def img2pixmap(self, img, detect=None, color=None):
        """ """
        image = QImage(img)
        image.convertToFormat(QImage.Format.Format_RGB32)
        imgArr = rgb_view(image)
        if detect is not None and color is not None:
            detect = self.hex2rgb(detect)
            target = self.hex2rgb(color)
            imgArr[np.where((imgArr == detect).all(axis=2))] = target
        image = array2qimage(imgArr)
        pixmap = QPixmap().fromImage(image)
        return pixmap

    @staticmethod
    def svg2pixmap(svg, color="black"):
        """ """
        img = QPixmap(svg)
        qp = QPainter(img)
        qp.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        qp.fillRect(img.rect(), QColor(color))
        qp.end()
        return img

    def svg2icon(self, svg, color="black"):
        """ """
        img = self.svg2pixmap(svg, color)
        return QIcon(img)

    def wIcon(self, gui=None, name=""):
        """ """
        if not gui or not name:
            return

        icon = self.svg2icon(f":/icon/{name}.svg", self.M_TER)
        gui.setIcon(icon)
        gui.setIconSize(QSize(16, 16))
        gui.setProperty("alignLeft", True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)

    def initUI(self):
        """ """
        self.setStyleSheet(self.mw4Style)
        self.setMouseTracking(True)
        self.setWindowIcon(QIcon(":/mw4.ico"))

    def prepareFileDialog(self, window=None, enableDir=False):
        """ """
        if not window:
            return None

        dlg = QFileDialog()
        dlg.setOptions(QFileDialog.Option.DontUseNativeDialog)
        dlg.setWindowIcon(QIcon(":/mw4.ico"))
        dlg.setStyleSheet(self.mw4Style)
        dlg.setViewMode(QFileDialog.ViewMode.List)
        dlg.setModal(True)
        if enableDir:
            dlg.setFilter(QDir.Filter.Files | QDir.Filter.AllDirs)
        else:
            dlg.setFilter(QDir.Filter.Files)

        width = 600
        height = 400
        ph = window.geometry().height()
        pw = window.geometry().width()
        px = window.geometry().x()
        py = window.geometry().y()

        dlg.setGeometry(
            px + int(0.5 * (pw - width)), py + int(0.5 * (ph - height)), width, height
        )
        return dlg

    @staticmethod
    def runDialog(dlg):
        """ """
        return dlg.exec()

    def messageDialog(self, parentWidget, title, question, buttons=None, iconType=0):
        """ """
        msg = QMessageBox()
        msg.setWindowModality(Qt.WindowModality.ApplicationModal)
        msg.setStyleSheet(self.mw4Style)
        msg.setTextFormat(Qt.TextFormat.AutoText)
        msg.setWindowTitle(title)
        icons = [
            ":/icon/question.svg",
            ":/icon/information.svg",
            ":/icon/warning.svg",
            ":/icon/question.svg",
        ]
        pixmap = QPixmap(icons[iconType]).scaled(64, 64)
        msg.setIconPixmap(pixmap)
        msg.setText(question)
        if buttons is None:
            msg.setStandardButtons(msg.StandardButton.Yes | msg.StandardButton.No)
            msg.setDefaultButton(msg.StandardButton.No)
        else:
            for button in buttons:
                msg.addButton(button, QMessageBox.ButtonRole.AcceptRole)
            msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        msg.show()
        x = parentWidget.x() + int((parentWidget.width() - msg.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - msg.height()) / 2)
        msg.move(x, y)
        reply = self.runDialog(msg)

        if buttons is None:
            if reply != msg.StandardButton.Yes:
                return False
            else:
                return True
        else:
            return reply

    def openFile(
        self,
        window=None,
        title="",
        folder=Path(""),
        filterSet=None,
        enableDir=False,
        multiple=False,
    ):
        """ """
        if multiple:
            default = []
        else:
            default = Path("")

        if not window:
            return default
        if not title:
            return default
        if not folder.is_dir():
            return default
        if not filterSet:
            return default

        dlg = self.prepareFileDialog(window=window, enableDir=enableDir)
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(str(folder))

        if multiple:
            dlg.setFileMode(QFileDialog.FileMode.ExistingFiles)
        else:
            dlg.setFileMode(QFileDialog.FileMode.ExistingFile)

        result = self.runDialog(dlg)
        if not result:
            return default

        if multiple:
            return [Path(f) for f in dlg.selectedFiles()]
        else:
            return Path(dlg.selectedFiles()[0])

    def saveFile(self, window=None, title="", folder="", filterSet=None, enableDir=False):
        """ """
        if not window:
            return Path("")
        if not title:
            return Path("")
        if not folder:
            return Path("")
        if not filterSet:
            return Path("")

        dlg = self.prepareFileDialog(window, enableDir)
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(str(folder))
        result = self.runDialog(dlg)
        if not result:
            return Path("")

        return Path(dlg.selectedFiles()[0])

    def openDir(self, window=None, title="", folder=""):
        """ """
        if not window:
            return Path("")
        if not title:
            return Path("")
        if not folder:
            return Path("")

        dlg = self.prepareFileDialog(window=window, enableDir=True)
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dlg.setWindowTitle(title)
        dlg.setDirectory(str(folder))
        dlg.setFileMode(QFileDialog.FileMode.Directory)
        result = self.runDialog(dlg)
        if not result:
            return Path("")

        return Path(dlg.selectedFiles()[0])

    def convertTime(self, value, fString):
        """ """
        isUTC = self.ui.unitTimeUTC.isChecked()
        if isUTC:
            return value.utc_strftime(fString)
        else:
            return value.astimezone(tzlocal()).strftime(fString)

    def timeZoneString(self):
        """ """
        if self.ui.unitTimeUTC.isChecked():
            return "(time is UTC)"
        else:
            return "(time is local)"

    @staticmethod
    def makePointer():
        """ """
        path = QPainterPath()
        path.moveTo(0, -1)
        path.lineTo(0, 1)
        path.moveTo(-1, 0)
        path.lineTo(1, 0)
        path.addEllipse(-0.1, -0.1, 0.2, 0.2)
        path.addEllipse(-0.3, -0.3, 0.6, 0.6)
        return path

    @staticmethod
    def makeSat():
        """ """
        path = QPainterPath()
        tr = QTransform()
        path.addRect(-0.35, -0.15, 0.1, 0.3)
        path.addRect(-0.2, -0.15, 0.1, 0.3)
        path.moveTo(-0.1, -0.15)
        path.lineTo(-0.1, -0.15)
        path.lineTo(0, 0)
        path.lineTo(-0.1, 0.15)
        path.lineTo(-0.1, 0.15)
        tr.rotate(180)
        path.addPath(tr.map(path))
        tr.rotate(45)
        path = tr.map(path)
        path.addEllipse(-0.05, -0.05, 0.1, 0.1)
        return path

    def positionWindow(self, config):
        """ """
        height = config.get("height", 600)
        width = config.get("width", 800)
        self.resize(width, height)
        x = config.get("winPosX", 0)
        y = config.get("winPosY", 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        x = max(x, 0)
        y = max(y, 0)
        if x != 0 and y != 0:
            self.move(x, y)
        return True

    @staticmethod
    def getTabIndex(tab, name):
        """ """
        tabWidget = tab.findChild(QWidget, name)
        tabIndex = tab.indexOf(tabWidget)
        return tabIndex

    @staticmethod
    def getTabAndIndex(tab, config, name):
        """ """
        config[name] = {"index": tab.currentIndex()}
        for index in range(tab.count()):
            config[name][f"{index:02d}"] = tab.widget(index).objectName()

    def setTabAndIndex(self, tab, config, name):
        """ """
        config = config.get(name, {})
        if not isinstance(config, dict):
            config = {}
        for index in reversed(range(tab.count())):
            nameTab = config.get(f"{index:02d}", None)
            if nameTab is None:
                continue
            tabIndex = self.getTabIndex(tab, nameTab)
            tab.tabBar().moveTab(tabIndex, index)
        tab.setCurrentIndex(config.get("index", 0))

    @staticmethod
    def positionCursorInTable(table, searchName):
        """ """
        result = table.findItems(searchName, Qt.MatchFlag.MatchExactly)
        if len(result) == 0:
            return
        item = result[0]
        index = table.row(item)
        table.selectRow(index)
        table.scrollToItem(item, QAbstractItemView.ScrollHint.EnsureVisible)
