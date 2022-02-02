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
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import logging
import datetime

# external packages
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton
from PyQt5.QtGui import QPalette, QIcon, QPixmap, QColor, QPainter, QImage
from PyQt5.QtCore import QSortFilterProxyModel, QDir, QObject, pyqtSignal
from PyQt5.QtCore import Qt, QSize, QEvent
from PyQt5.QtTest import QTest
import numpy as np
from qimage2ndarray import rgb_view, array2qimage

# local imports
from gui.utilities.stylesQtCss import Styles
from gui.utilities.toolsMatplotlib import ToolsMatplotlib
from mountcontrol.convert import formatHstrToText, formatDstrToText

__all__ = [
    'MWidget',
    'FileSortProxyModel',
    'QMultiWait',
    'sleepAndEvents',
]


def sleepAndEvents(value):
    """
    :param value: wait time in msec
    :return:
    """
    QTest.qWait(value)
    return True


class FileSortProxyModel(QSortFilterProxyModel):
    """
    FileSortProxyModel enables a proxy solution for reversing the order of all
    file dialogues. The sorting is now Descending meaning the last added files
    will be on top. This is don by just overwriting the sort method
    """
    def sort(self, column, order):
        self.sourceModel().sort(0, Qt.DescendingOrder)


class QMultiWait(QObject):
    """
    QMultiWaitable implements a signal collection class for waiting of entering
    multiple signals before firing the "AND" relation of all signals.
    derived from:

    https://stackoverflow.com/questions/21108407/qt-how-to-wait-for-multiple-signals

    in addition all received signals could be reset
    """
    ready = pyqtSignal()
    log = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()
        self.waitable = set()
        self.waitready = set()

    def addWaitableSignal(self, signal):
        if signal not in self.waitable:
            self.waitable.add(signal)
            signal.connect(self.checkSignal)

    def checkSignal(self):
        sender = self.sender()
        self.waitready.add(sender)
        self.log.debug(f'QMultiWait [{self}]: [{self.waitready}]')

        if len(self.waitready) == len(self.waitable):
            self.log.debug(f'Firing QMultiWait for [{self}]')
            self.ready.emit()

    def resetSignals(self):
        self.waitready = set()

    def clear(self):
        for signal in self.waitable:
            signal.disconnect(self.checkSignal)

        self.waitable = set()
        self.waitready = set()


class QCustomTableWidgetItem(QTableWidgetItem):
    """
    This class reimplements the comparison for item, which are normally float
    values as the standard sorting in this item only supports strings.
    """
    def __init__(self, value):
        super().__init__(value)

    def __lt__(self, other):
        if (isinstance(other, QCustomTableWidgetItem)):
            selfData = self.data(Qt.EditRole)
            if selfData == '':
                selfDataValue = 99
            else:
                selfDataValue = float(selfData)
            otherData = other.data(Qt.EditRole)
            if otherData == '':
                otherDataValue = 99
            else:
                otherDataValue = float(otherData)
            return selfDataValue < otherDataValue
        else:
            return QTableWidgetItem.__lt__(self, other)


class MWidget(QWidget, Styles, ToolsMatplotlib):
    """
    MWidget defines the common parts for all windows used in MountWizzard 4 and
    extends the standard widgets. All widgets configs which are used mor than
    one time are centralized in this class.

    For the File dialogues, the original widgets are used, but with the removal
    of some features to make them simpler. As one optimization they always show
    the files and directories in descending order.

    The styles of the widgets are defined separately in a css looking
    stylesheet. The standard screen size will be 800x600 pixel for all windows,
    but except for the main one are sizable.
    """

    __all__ = ['MWidget',
               ]

    def __init__(self):
        super().__init__()

        self.palette = QPalette()
        self.initUI()
        self.screenSizeX = QDesktopWidget().screenGeometry().width()
        self.screenSizeY = QDesktopWidget().screenGeometry().height()
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        newFlag = Qt.CustomizeWindowHint | Qt.WindowSystemMenuHint
        newFlag = newFlag | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint
        self.setWindowFlags(self.windowFlags() | newFlag)
        self.setWindowIcon(QIcon(':/icon/mw4.png'))

    @staticmethod
    def findIndexValue(ui, searchString, relaxed=False):
        """
        :param ui:
        :param searchString:
        :param relaxed:
        :return:
        """
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

    def saveWindowAsPNG(self, window):
        """
        :param window:
        :return:
        """
        name = window.windowTitle().replace(' ', '_')
        timeTrigger = datetime.datetime.now(datetime.timezone.utc)
        timeTag = timeTrigger.strftime('%Y-%m-%d-%H-%M-%S')
        path = self.app.mwGlob['workDir']
        fullFileName = f'{path}/{timeTag}-{name}.png'
        self.log.info(f'Screenshot: [{fullFileName}]')
        window.grab().save(fullFileName)
        return True

    def saveAllWindowsAsPNG(self):
        """
        :return:
        """
        windows = self.app.uiWindows
        self.saveWindowAsPNG(self.app.mainW)
        for window in windows:
            obj = windows[window]['classObj']
            if obj:
                self.saveWindowAsPNG(obj)
        return True

    def keyPressEvent(self, keyEvent):
        """
        Pressing F5 makes a screen copy of the actual window
        Pressing F6 makes a screen copy of all open windows
        :param keyEvent:
        :return:
        """
        if keyEvent.key() == 16777268:
            self.saveWindowAsPNG(self)
            return
        elif keyEvent.key() == 16777269:
            self.saveAllWindowsAsPNG()
            return
        super().keyPressEvent(keyEvent)

    def img2pixmap(self, img, detect=None, color=None):
        """
        :param img:
        :param detect:
        :param color:
        :return:
        """
        image = QImage(img)
        image.convertToFormat(QImage.Format_RGB32)
        imgArr = rgb_view(image)
        if detect is not None and color is not None:
            detect = self.hex2rgb(detect)
            target = self.hex2rgb(color)
            imgArr[np.where((imgArr == detect).all(axis=2))] = target
        image = array2qimage(imgArr)
        pixmap = QPixmap().fromImage(image)
        return pixmap

    @staticmethod
    def svg2pixmap(svg, color='black'):
        """
        :param svg:
        :param color:
        :return:
        """
        img = QPixmap(svg)
        qp = QPainter(img)
        qp.setCompositionMode(QPainter.CompositionMode_SourceIn)
        qp.fillRect(img.rect(), QColor(color))
        qp.end()
        return img

    def svg2icon(self, svg, color='black'):
        """
        :param svg:
        :param color:
        :return:
        """
        img = self.svg2pixmap(svg, color)
        return QIcon(img)

    def wIcon(self, gui=None, name=''):
        """
        widget icon adds an icon to a gui element like an button.

        :param      gui:        gui element, which will be expanded by an icon
        :param      name:       icon to be added
        :return:    true for test purpose
        """
        if not gui:
            return False
        if not name:
            return False

        icon = self.svg2icon(f':/icon/{name}.svg', self.M_BLUE)
        gui.setIcon(icon)
        gui.setIconSize(QSize(16, 16))
        gui.setProperty('alignLeft', True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)
        return True

    @staticmethod
    def changeIconColor(widget, color):
        """
        :param widget:
        :param color:
        :return:
        """
        icon = widget.icon()
        pixmap = icon.pixmap(icon.actualSize(QSize(64, 64)))
        mask = pixmap.createMaskFromColor(QColor('transparent'), Qt.MaskInColor)
        pixmap.fill(QColor(color))
        pixmap.setMask(mask)
        widget.setIcon(QIcon(pixmap))
        return True

    def initUI(self):
        """
        init_UI makes the basic initialisation of the GUI. is sets the window
        flags and sets the handling of the window. is as well fixes the windows
        size (unless a windows will be scalable later on. in addition the
        appropriate style sheet for mac and non mac will be selected and used.

        :return:    true for test purpose
        """
        self.setStyleSheet(self.mw4Style)
        self.setMouseTracking(True)
        self.setWindowIcon(QIcon(':/mw4.ico'))
        return True

    def changeStyleDynamic(self, widget=None, widgetProperty=None, value=None):
        """
        changeStyleDynamic changes the stylesheet of a given ui element and
        makes it visible. therefore the element has to be unpolished and
        polished again.

        :param      widget: widget element, where the stylesheet has to
                            be changed
        :param      widgetProperty: stylesheet attribute which has to be
                                    changes
        :param      value:  new value of the attribute
        :return:    true for test purpose
        """
        if not widget:
            return False
        if not widgetProperty:
            return False
        if value is None:
            return False
        if widget.property(widgetProperty) == value:
            return True

        if isinstance(widget, QPushButton):
            if widgetProperty == 'running' and value:
                self.changeIconColor(widget, self.M_BACK)
            elif widgetProperty == 'running' and not value:
                self.changeIconColor(widget, self.M_BLUE)

        widget.style().unpolish(widget)
        widget.setProperty(widgetProperty, value)
        widget.style().polish(widget)
        return True

    @staticmethod
    def extractNames(names=''):
        """
        extractNames splits a given path to basename and extension
        if the input is a multiple list, there will be as return values a
        multiple list as well, otherwise single values

        :param      names:   full path of file (s)
        :return:    short:  basename without extension
                    ext:    extension
                    name:   name
        """
        if not names:
            return '', '', ''
        if not isinstance(names, list):
            return '', '', ''

        shortList = list()
        extList = list()
        nameList = list()

        for name in names:
            if name:
                short, ext = os.path.splitext(name)
                short = os.path.basename(short)

            else:
                short = ''
                ext = ''

            nameList.append(os.path.abspath(name))
            shortList.append(short)
            extList.append(ext)

        if len(names) == 1:
            return nameList[0], shortList[0], extList[0]
        else:
            return nameList, shortList, extList

    def prepareFileDialog(self, window=None, enableDir=False, reverseOrder=False):
        """
        prepareFileDialog does some tweaking of the standard file dialogue
        widget for geometry and general settings. it also removes some parts and
        makes the dialog modal.

        :param window:  parent class
        :param enableDir:   allows dir selection in file box
        :param reverseOrder:   file selection z->a
        :return:        dlg, the dialog widget
        """
        if not window:
            return None

        dlg = QFileDialog()
        dlg.setOptions(QFileDialog.DontUseNativeDialog)
        dlg.setWindowIcon(QIcon(':/mw4.ico'))
        dlg.setStyleSheet(self.mw4Style)
        dlg.setViewMode(QFileDialog.List)
        dlg.setModal(True)
        if reverseOrder:
            dlg.setProxyModel(FileSortProxyModel(self))

        if enableDir:
            dlg.setFilter(QDir.Files | QDir.AllDirs)
        else:
            dlg.setFilter(QDir.Files)

        width = 600
        height = 400
        ph = window.geometry().height()
        pw = window.geometry().width()
        px = window.geometry().x()
        py = window.geometry().y()

        dlg.setGeometry(px + int(0.5 * (pw - width)),
                        py + int(0.5 * (ph - height)),
                        width,
                        height)
        return dlg

    @staticmethod
    def runDialog(dlg):
        """
        :param dlg:
        :return: result
        """
        return dlg.exec_()

    def messageDialog(self, parentWidget, title, question):
        """
        :param parentWidget:
        :param title:
        :param question:
        :return: OK
        """
        msg = QMessageBox()
        msg.setWindowModality(Qt.ApplicationModal)
        msg.setStyleSheet(self.mw4Style)
        msg.setTextFormat(Qt.AutoText)
        msg.setWindowTitle(title)
        pixmap = QPixmap(':/icon/question.svg').scaled(64, 64)
        msg.setIconPixmap(pixmap)
        msg.setText(question)
        msg.setStandardButtons(msg.Yes | msg.No)
        msg.setDefaultButton(msg.No)
        msg.show()
        x = parentWidget.x() + int((parentWidget.width() - msg.width()) / 2)
        y = parentWidget.y() + int((parentWidget.height() - msg.height()) / 2)
        msg.move(x, y)
        reply = self.runDialog(msg)

        if reply != msg.Yes:
            return False
        else:
            return True

    def openFile(self,
                 window=None,
                 title='',
                 folder='',
                 filterSet=None,
                 enableDir=False,
                 multiple=False,
                 reverseOrder=False):
        """
        openFile handles a single file select with filter in a non native format.

        :param window:      parent window class
        :param title:       title for the file dialog
        :param folder:      starting folder for searching the file
        :param filterSet:   file extension filter
        :param enableDir:   allows dir selection in file box
        :param multiple :   allows multiple selection in file box
        :param reverseOrder :   file selection z->a
        :return:            name: full path for file else empty
                            short: just file name without extension
                            ext: extension of the file
        """
        if not window:
            return '', '', ''
        if not title:
            return '', '', ''
        if not folder:
            return '', '', ''
        if not filterSet:
            return '', '', ''

        dlg = self.prepareFileDialog(window=window,
                                     enableDir=enableDir,
                                     reverseOrder=reverseOrder)
        dlg.setAcceptMode(QFileDialog.AcceptOpen)

        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(folder)

        if multiple:
            dlg.setFileMode(QFileDialog.ExistingFiles)
        else:
            dlg.setFileMode(QFileDialog.ExistingFile)

        result = self.runDialog(dlg)
        if not result:
            return '', '', ''

        filePath = dlg.selectedFiles()
        full, short, ext = self.extractNames(names=filePath)
        return full, short, ext

    def saveFile(self,
                 window=None,
                 title='',
                 folder='',
                 filterSet=None,
                 enableDir=False):
        """
        saveFile handles a single file save with filter in a non native format.

        :param window:      parent window class
        :param title:       title for the file dialog
        :param folder:      starting folder for searching the file
        :param filterSet:   file extension filter
        :param enableDir:   allows dir selection in file box
        :return:            name: full path for file else empty
                            short: just file name without extension
                            ext: extension of the file
        """
        if not window:
            return '', '', ''
        if not title:
            return '', '', ''
        if not folder:
            return '', '', ''
        if not filterSet:
            return '', '', ''

        dlg = self.prepareFileDialog(window, enableDir)
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(folder)
        result = self.runDialog(dlg)
        if not result:
            return '', '', ''

        filePath = dlg.selectedFiles()
        full, short, ext = self.extractNames(names=filePath)
        return full, short, ext

    def openDir(self,
                window=None,
                title='',
                folder=''):
        """
        openFile handles a single file select with filter in a non native format.

        :param window:      parent window class
        :param title:       title for the file dialog
        :param folder:      starting folder for searching the file
        :return:            name: full path for file else empty
                            short: just file name without extension
                            ext: extension of the file
        """
        if not window:
            return '', '', ''
        if not title:
            return '', '', ''
        if not folder:
            return '', '', ''

        dlg = self.prepareFileDialog(window=window, enableDir=True)
        dlg.setAcceptMode(QFileDialog.AcceptOpen)
        dlg.setWindowTitle(title)
        dlg.setDirectory(folder)
        dlg.setFileMode(QFileDialog.DirectoryOnly)
        result = self.runDialog(dlg)
        if not result:
            return '', '', ''

        filePath = dlg.selectedFiles()
        full, short, ext = self.extractNames(names=filePath)
        return full, short, ext

    @staticmethod
    def clickable(widget=None):
        """
        It uses one filter object per label, which is created when the
        clickable() function is called with the widget that is to be
        click-enabled. The function returns a clicked() signal that actually
        belongs to the filter object. The caller can connect this signal to a
        suitable callable object.

        :param widget:      widget for what the event filter works
        :return:            filtered event
        """
        if not widget:
            return None

        class MouseClickEventFilter(QObject):
            clicked = pyqtSignal(object)

            def eventFilter(self, obj, event):
                if event.type() not in [QEvent.MouseButtonRelease,
                                        QEvent.FocusIn]:
                    return False

                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit(widget)
                        return True

                return False

        clickEventFilter = MouseClickEventFilter(widget)
        widget.installEventFilter(clickEventFilter)
        return clickEventFilter.clicked

    @staticmethod
    def guiSetText(ui, formatElement, value=None):
        """
        :param ui:
        :param formatElement:
        :param value:
        :return: True for test purpose
        """
        if not ui:
            return False
        if not formatElement:
            return False
        if value is None:
            text = '-'
        elif isinstance(value, (list, np.ndarray)) and len(value) == 0:
            text = '-'
        elif formatElement.startswith('HSTR'):
            text = formatHstrToText(value)
        elif formatElement.startswith('DSTR'):
            text = formatDstrToText(value)
        elif formatElement.startswith('D'):
            formatStr = '{0:' + formatElement.lstrip('D') + '}'
            text = formatStr.format(value.degrees)
        elif formatElement.startswith('H'):
            formatStr = '{0:' + formatElement.lstrip('H') + '}'
            text = formatStr.format(value.hours)
        elif value == 'E':
            text = 'EAST'
        elif value == 'W':
            text = 'WEST'
        elif isinstance(value, bool):
            if value:
                text = 'ON'
            else:
                text = 'OFF'
        else:
            formatStr = '{0:' + formatElement + '}'
            text = formatStr.format(value)

        ui.setText(text)
        return True

    def guiSetStyle(self, ui, pStyle='', value=None, pVals=None):
        """
        :param ui:
        :param pStyle:
        :param value:
        :param pVals:
        :return:
        """
        if pVals is None:
            pVals = ['', '', '']
        if not pStyle:
            return False
        if value is None:
            pVal = pVals[0]
        elif value:
            pVal = pVals[1]
        else:
            pVal = pVals[2]

        self.changeStyleDynamic(ui, pStyle, pVal)
        return True

    @staticmethod
    def returnDriver(sender, searchDict, addKey=''):
        """
        returnDriver takes the sender widget from a gui interaction and compares
        is to the widget objects of a search dicts to retrieve is original name.
        therefore we need to swap key value pais in the search dict as we make a
        reverse search.
        in addition to make it more usable the search dict might have some sub
        dicts where to find the gui elements. if given, the will be extracted on
        the forehand.

        :param sender:
        :param searchDict:
        :param addKey:
        :return:
        """
        if addKey:
            searchD = dict([(key, value[addKey]) for key, value in searchDict.items()])
        else:
            searchD = searchDict

        searchD = dict([(value, key) for key, value in searchD.items()])
        driver = searchD.get(sender, '')
        return driver

    def checkUpdaterOK(self):
        """
        :return:
        """
        if not self.app.automation:
            self.app.message.emit('No automation enabled - upload not possible', 2)
            return ''

        if not self.app.automation.installPath:
            t = 'No 10micron updater available - upload not possible'
            self.app.message.emit(t, 2)
            return ''

        return self.app.automation.updaterApp
