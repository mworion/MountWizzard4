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
import platform
import os
import re

# external packages
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QFileDialog, QMessageBox
from PyQt5.QtGui import QPalette, QIcon, QPixmap
from PyQt5.QtCore import QSortFilterProxyModel, QDir, QObject, pyqtSignal
from PyQt5.QtCore import Qt, QSize, QEvent
from skyfield.api import Angle
import numpy as np

# local imports
from gui.utilities.stylesQtCss import Styles
from gui.utilities.toolsMatplotlib import ToolsMatplotlib
from mountcontrol.convert import sexagesimalizeToInt

__all__ = [
    'MWidget',
    'FileSortProxyModel',
    'QMultiWait',
]


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

        if len(self.waitready) == len(self.waitable):
            self.ready.emit()

    def resetSignals(self):
        self.waitready = set()

    def clear(self):
        for signal in self.waitable:
            signal.disconnect(self.checkSignal)

        self.waitable = set()
        self.waitready = set()


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
    def wIcon(gui=None, name=''):
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

        icon = QIcon(f':/icon/{name}.svg')
        gui.setIcon(icon)
        gui.setIconSize(QSize(16, 16))
        gui.setProperty('alignLeft', True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)
        return True

    def getStyle(self):
        """
        getStyle return the actual stylesheet for the used platform.
        As the font sizes vary between Darwin and Windows / Ubuntu there were
        two sets of stylesheets used. a basic stylesheet adds undifferentiated
        properties.

        :return:    actual stylesheet string
        """
        if platform.system() == 'Darwin':
            return self.MAC_STYLE + self.BASIC_STYLE
        else:
            return self.NON_MAC_STYLE + self.BASIC_STYLE

    def initUI(self):
        """
        init_UI makes the basic initialisation of the GUI. is sets the window
        flags and sets the handling of the window. is as well fixes the windows
        size (unless a windows will be scalable later on. in addition the
        appropriate style sheet for mac and non mac will be selected and used.

        :return:    true for test purpose
        """
        self.setWindowFlags(self.windowFlags())
        style = self.getStyle()
        self.setStyleSheet(style)
        self.setMouseTracking(True)
        self.setWindowIcon(QIcon(':/mw4.ico'))
        return True

    @staticmethod
    def changeStyleDynamic(widget=None, widgetProperty=None, value=None):
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
        dlg.setStyleSheet(self.getStyle())
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
        msg.setStyleSheet(self.getStyle())
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

        class MouseDoubleClickEventFilter(QObject):
            clicked = pyqtSignal(object)

            def eventFilter(self, obj, event):
                if obj != widget:
                    return False

                if event.type() not in [QEvent.MouseButtonRelease,
                                        QEvent.FocusIn]:
                    return False

                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit(widget)
                        return True

                return False

        doubleClickEventFilter = MouseDoubleClickEventFilter(widget)
        widget.installEventFilter(doubleClickEventFilter)
        return doubleClickEventFilter.clicked

    def guiSetText(self, ui, formatElement, value=None):
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
            text = self.formatHstrToText(value)
        elif formatElement.startswith('DSTR'):
            text = self.formatDstrToText(value)
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

    def guiSetStyle(self, ui, pStyle='', value=None, pVals=['', '', '']):
        """
        :param ui:
        :param pStyle:
        :param value:
        :param pVals:
        :return:
        """
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

    @staticmethod
    def formatLatLonToAngle(value, pf):
        """
        :param value:
        :param pf: double character, first indicates the negative sign
        :return:
        """
        if value is None:
            return None

        value = value.strip()
        p1 = re.compile(r'(\d{1,3})([' + pf + r'])\s*(\d\d)?\s*(\d\d)?[.,]?(\d*)?')
        p2 = re.compile(r'([-+]?)(\d{1,3})[.,]?(\d*)?')
        isSexagesimal = p1.fullmatch(value) is not None
        isFloat = p2.fullmatch(value) is not None

        elements = p2.split(value)
        if isFloat:
            angle = float(value.replace(',', '.'))

        elif isSexagesimal:
            angle = float(elements[2])
            if len(elements) > 5:
                angle += float(elements[6]) / 60
            if len(elements) > 9:
                angle += float(elements[10]) / 3600
            if elements[4].startswith(pf[0]):
                angle = -angle
        else:
            return None

        if 'N' in pf:
            maxAbs = 90
        else:
            maxAbs = 180

        if angle > maxAbs:
            return None
        elif angle < -maxAbs:
            return None

        angle = Angle(degrees=angle)
        return angle

    def convertLatToAngle(self, value):
        """
        :param value:
        :return:
        """
        angle = self.formatLatLonToAngle(value, 'SN')
        return angle

    def convertLonToAngle(self, value):
        """
        :param value:
        :return:
        """
        angle = self.formatLatLonToAngle(value, 'WE')
        return angle

    @staticmethod
    def convertRaToAngle(value):
        """
        :param value:
        :return:
        """
        if value is None:
            return None

        value = value.strip()
        p1 = re.compile(r'([+-]?)(\d{1,3})H\s*(\d\d)?\s*(\d\d)?[.,]?(\d*)?')
        p2 = re.compile(r'([+-]?)(\d{1,3})\s+(\d\d)?\s*(\d\d)?[.,]?(\d*)?')
        p3 = re.compile(r'([+-]?)(\d{1,3})[.,]?(\d*)?')
        isP1 = p1.fullmatch(value) is not None
        isP2 = p2.fullmatch(value) is not None
        isSexagesimal = isP1 or isP2
        isFloat = p3.fullmatch(value) is not None

        if isP1:
            elements = p1.split(value)
        elif isP2:
            elements = p2.split(value)
        else:
            elements = ''

        if isFloat:
            angle = float(value.replace(',', '.'))
        elif isSexagesimal:
            angle = float(elements[2])
            if elements[3] is not None:
                angle += float(elements[3]) / 60
            if elements[4] is not None:
                angle += float(elements[4]) / 3600
        else:
            return None

        if angle >= 24:
            return None
        if angle < 0:
            return None
        if isFloat:
            angle = Angle(hours=angle / 360 * 24)
        elif isSexagesimal:
            angle = Angle(hours=angle)

        return angle

    @staticmethod
    def convertDecToAngle(value):
        """
        :param value:
        :return:
        """
        if value is None:
            return None

        value = value.strip()
        p1 = re.compile(r'([+-]?)(\d{1,3})Deg\s*(\d\d)?\s*(\d\d)?[.,]?(\d*)?')
        p2 = re.compile(r'([+-]?)(\d{1,3})\s+(\d\d)?\s*(\d\d)?[.,]?(\d*)?')
        p3 = re.compile(r'([+-]?)(\d{1,3})[.,]?(\d*)?')
        isP1 = p1.fullmatch(value) is not None
        isP2 = p2.fullmatch(value) is not None
        isSexagesimal = isP1 or isP2
        isFloat = p3.fullmatch(value) is not None

        if isP1:
            elements = p1.split(value)
        elif isP2:
            elements = p2.split(value)
        else:
            elements = ''

        if isFloat:
            angle = float(value.replace(',', '.'))

        elif isSexagesimal:
            angle = float(elements[2])
            if elements[3] is not None:
                angle += float(elements[3]) / 60
            if elements[4] is not None:
                angle += float(elements[4]) / 3600
            if elements[1].startswith('-'):
                angle = -angle
        else:
            return None

        if angle > 90:
            return None
        if angle < -90:
            return None

        angle = Angle(degrees=angle)
        return angle

    @staticmethod
    def formatHstrToText(angle):
        """
        :param angle:
        :return:
        """
        sgn, h, m, s, frac = sexagesimalizeToInt(angle.hours, 0)
        text = f'{h:02d} {m:02d} {s:02d}'
        return text

    @staticmethod
    def formatDstrToText(angle):
        """
        :param angle:
        :return:
        """
        sgn, h, m, s, frac = sexagesimalizeToInt(angle.degrees, 0)
        sign = '+' if sgn >= 0 else '-'
        text = f'{sign}{h:02d} {m:02d} {s:02d}'
        return text

    @staticmethod
    def formatLatToText(angle):
        """
        :param angle:
        :return:
        """
        sgn, h, m, s, frac = sexagesimalizeToInt(angle.degrees, 0)
        sign = 'N' if sgn >= 0 else 'S'
        text = f'{h:02d}{sign} {m:02d} {s:02d}'
        return text

    @staticmethod
    def formatLonToText(angle):
        """
        :param angle:
        :return:
        """
        sgn, h, m, s, frac = sexagesimalizeToInt(angle.degrees, 0)
        sign = 'E' if sgn >= 0 else 'W'
        text = f'{h:03d}{sign} {m:02d} {s:02d}'
        return text
