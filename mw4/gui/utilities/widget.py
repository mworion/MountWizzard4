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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform
import os
from threading import Lock
import bisect

# external packages
import numpy as np
from PyQt5.QtWidgets import QWidget, QDesktopWidget, qApp, QFileDialog
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QPalette, QIcon
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QDir, QObject, pyqtSignal, QEvent
from PyQt5.QtCore import QSize
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# local imports
from base.loggerMW import CustomLogger
from gui.utilities import styles

__all__ = [
    'MWidget',
    'FileSortProxyModel',
    'QMultiWait',
]


class FileSortProxyModel(QSortFilterProxyModel):
    """
    FileSortProxyModel enables a proxy solution for reversing the order of all file dialogues.
    The sorting is now Descending meaning the last added files will be on top.
    This is don by just overwriting the sort method
    """

    def sort(self, column, order):
        self.sourceModel().sort(0, Qt.DescendingOrder)


class QMultiWait(QObject):
    """
    QMultiWaitable implements a signal collection class for waiting of entering multiple
    signals before firing the "AND" relation of all signals.
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


class MWidget(QWidget, styles.MWStyles):
    """
    MWidget defines the common parts for all windows used in MountWizzard 4 and extends the
    standard widgets. All widgets configs which are used mor than one time are centralized
    in this class.

    For the File dialogues, the original widgets are used, but with the removal of some
    features to make them simpler. As one optimization they always show the files and
    directories in descending order.

    The styles of the widgets are defined separately in a css looking stylesheet. The
    standard screen size will be 800x600 pixel for all windows, but except for the main
    one are sizable.
    """

    __all__ = ['MWidget',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self):
        super().__init__()

        self.palette = QPalette()
        self.initUI()
        self.screenSizeX = QDesktopWidget().screenGeometry().width()
        self.screenSizeY = QDesktopWidget().screenGeometry().height()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowFlags(self.windowFlags() |
                            Qt.CustomizeWindowHint |
                            Qt.WindowSystemMenuHint |
                            Qt.WindowMinimizeButtonHint |
                            Qt.WindowMaximizeButtonHint)

    @staticmethod
    def wIcon(gui=None, icon=None):
        """
        widget icon adds an icon to a gui element like an button.

        :param      gui:        gui element, which will be expanded by an icon
        :param      icon:       icon to be added
        :return:    true for test purpose
        """

        if not gui:
            return False

        if not icon:
            return False

        if not isinstance(icon, QIcon):
            iconset = qApp.style().standardIcon(icon)
            icon = QIcon(iconset)

        gui.setIcon(icon)
        gui.setProperty('iconset', True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)
        gui.setIconSize(QSize(16, 16))

        return True

    def getStyle(self):
        """
        getStyle return the actual stylesheet for the used platform.
        As the font sizes vary between Darwin and Windows / Ubuntu there were two sets of
        stylesheets used. a basic staylsheet adds undifferentiated properties.

        :return:    actual stylesheet string
        """

        if platform.system() == 'Darwin':
            return self.MAC_STYLE + self.BASIC_STYLE

        else:
            return self.NON_MAC_STYLE + self.BASIC_STYLE

    def initUI(self):
        """
        init_UI makes the basic initialisation of the GUI. is sets the window flags
        and sets the handling of the window. is as well fixes the windows size (unless
        a windows will be scalable later on. in addition the appropriate style sheet
        for mac and non mac will be selected and used.

        :return:    true for test purpose
        """

        self.setWindowFlags(self.windowFlags())
        style = self.getStyle()
        self.setStyleSheet(style)
        self.setMouseTracking(True)
        self.setWindowIcon(QIcon(':/mw4.ico'))

        return True

    @staticmethod
    def changeStyleDynamic(widget=None, item=None, value=None):
        """
        changeStyleDynamic changes the stylesheet of a given uii element and makes it
        visible. therefore the element has to be unpolished and polished again.

        :param      widget:     widget element, where the stylesheet has to be changed
        :param      item:   stylesheet attribute which has to be changes
        :param      value:  new value of the attribute
        :return:    true for test purpose
        """

        if not widget:
            return False

        if not item:
            return False

        if value is None:
            return False

        widget.style().unpolish(widget)
        widget.setProperty(item, value)
        widget.style().polish(widget)

        return True

    @staticmethod
    def extractNames(names=''):
        """
        extractNames splits a given path to basename and extension
        if the input is a multiple list, there will be as return values a multiple list
        as well, otherwise single values

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
        prepareFileDialog does some tweaking of the standard file dialogue widget for geometry
        and general settings. it also removes some parts ans makes the dialog modal.

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
        separated from method for better testing !

        :param dlg:
        :return: result
        """

        return dlg.exec_()

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
        It uses one filter object per label, which is created when the clickable()
        function is called with the widget that is to be click-enabled. The function
        returns a clicked() signal that actually belongs to the filter object. The caller
        can connect this signal to a suitable callable object.

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

                if event.type() != QEvent.MouseButtonRelease:
                    return False

                if obj.rect().contains(event.pos()):
                    self.clicked.emit(widget)
                    return True

                return False

        doubleClickEventFilter = MouseDoubleClickEventFilter(widget)
        widget.installEventFilter(doubleClickEventFilter)

        return doubleClickEventFilter.clicked

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

        else:
            formatStr = '{0:' + formatElement + '}'
            text = formatStr.format(value)

        ui.setText(text)

        return True

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

            if indexValue is None:
                continue

            if relaxed:
                if searchString in indexValue:
                    return index

            else:
                if indexValue.startswith(searchString):
                    return index

        return 0

    @staticmethod
    def embedMatplot(widget=None, constrainedLayout=True):
        """
        embedMatplot provides the wrapper to use matplotlib drawings inside a pyqt5
        application gui. you call it with the parent widget, which is linked to matplotlib
        canvas of the same size. the background is set to transparent, so you could layer
        multiple figures on top.

        :param      widget:         parent ui element, which is the reference for embedding
        :param      constrainedLayout:
        :return:    staticCanvas:   matplotlib reference as parent for figures
        """

        if not widget:
            return None

        widget.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        staticCanvas = FigureCanvas(Figure(dpi=75,
                                           facecolor='None',
                                           frameon=False,
                                           tight_layout=constrainedLayout,
                                           )
                                    )
        FigureCanvasQTAgg.updateGeometry(staticCanvas)
        layout.addWidget(staticCanvas)
        staticCanvas.setParent(widget)

        return staticCanvas

    def generatePolar(self, widget=None, title='', horizon=False, showAxes=True):
        """

        :param widget:
        :param title:
        :param horizon:
        :param showAxes:
        :return:
        """

        if widget is None:
            return None, None

        if not hasattr(widget, 'figure'):
            return None, None

        lock = Lock()

        if showAxes:
            color = self.M_BLUE
            colorGrid = self.M_GREY

        else:
            color = self.M_TRANS
            colorGrid = self.M_TRANS

        with lock:
            figure = widget.figure

            if figure.axes:
                axe = figure.axes[0]
                axe.cla()

            else:
                figure.clf()
                axe = figure.add_subplot(1, 1, 1, polar=True, facecolor='None')

            axe.grid(True, color=colorGrid)

            if title:
                axe.set_title(title, color=color, fontweight='bold', pad=15)

            axe.set_xlabel('', color=color, fontweight='bold', fontsize=12)
            axe.set_ylabel('', color=color, fontweight='bold', fontsize=12)
            axe.tick_params(axis='x', colors=color, labelsize=12)
            axe.tick_params(axis='y', colors=color, labelsize=12)
            axe.set_theta_zero_location('N')
            axe.set_rlabel_position(45)
            axe.set_theta_direction(-1)

            # ticks have to be set before labels to be sure to have them positioned correctly
            axe.set_xticks(np.radians([0, 45, 90, 135, 180, 225, 270, 315]))
            axe.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

            if not horizon:
                return axe, figure

            axe.set_ylim(0, 90)
            axe.set_yticks(range(0, 91, 15))
            axe.set_yticklabels(['', '75', '60', '45', '30', '15', ''])

            return axe, figure

    def generateFlat(self, widget=None, title='', horizon=False, showAxes=True):
        """

        :param widget:
        :param title:
        :param horizon:
        :param showAxes:
        :return:
        """

        if widget is None:
            return None, None

        if not hasattr(widget, 'figure'):
            return None, None

        lock = Lock()

        if showAxes:
            color = self.M_BLUE
            colorGrid = self.M_GREY

        else:
            color = self.M_TRANS
            colorGrid = self.M_TRANS

        with lock:
            figure = widget.figure

            if figure.axes:
                axe = figure.axes[0]
                axe.cla()

            else:
                figure.clf()
                axe = figure.add_subplot(1, 1, 1, facecolor='None')

            axe.spines['bottom'].set_color(color)
            axe.spines['top'].set_color(color)
            axe.spines['left'].set_color(color)
            axe.spines['right'].set_color(color)
            axe.grid(showAxes, color=colorGrid)

            if title:
                axe.set_title(title, color=color, fontweight='bold', pad=15)

            axe.set_xlabel('', color=color, fontweight='bold', fontsize=12)
            axe.set_ylabel('', color=color, fontweight='bold', fontsize=12)
            axe.tick_params(axis='x', colors=color, labelsize=12)
            axe.tick_params(axis='y', colors=color, labelsize=12)

            if not horizon:
                return axe, figure

            axe.set_xlim(0, 360)
            axe.set_ylim(0, 90)

            axe.set_xticks(np.arange(0, 361, 45))
            axe.set_xticklabels(['0 N', '45 NE', '90 E', '135 SE', '180 S', '225 SW', '270 W',
                                 '315 NW', '360 N'])
            axe.set_xlabel('Azimuth [degrees]', color=color, fontweight='bold', fontsize=12)
            axe.set_ylabel('Altitude [degrees]', color=color, fontweight='bold', fontsize=12)

            return axe, figure

    @staticmethod
    def returnDriver(sender, searchDict, addKey=''):
        """
        returnDriver takes the sender widget from a gui interaction and compares is to the
        widget objects of a search dicts to retrieve is original name.
        therefore we need to swap key value pais in the search dict as we make a reverse
        search.
        in addition to make it more usable the search dict might have some sub dicts where
        to find the gui elements. if given, the will be extracted on the forehand.

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
    def getIndexPoint(event=None, plane=None, epsilon=2):
        """
        getIndexPoint returns the index of the point which is nearest to the coordinate
        of the mouse click when the click is in distance epsilon of the points. otherwise
        no index will be returned.

        :param event: data of the mouse clicked event
        :param plane: coordinates as tuples (alt, az)
        :param epsilon:
        :return: index or none
        """

        if event is None:
            return None

        if plane is None:
            return None

        if len(plane) == 0:
            return 0

        xt = np.asarray([i[1] for i in plane])
        yt = np.asarray([i[0] for i in plane])
        d = np.sqrt((xt - event.xdata)**2 / 4 + (yt - event.ydata)**2)
        index = d.argsort()[:1][0]

        if d[index] >= epsilon:
            return None

        index = int(index)

        return index

    @staticmethod
    def getIndexPointX(event=None, plane=None):
        """
        getIndexPointX returns the index of the point which has a x coordinate closest to
        the left of the x coordinate of the mouse click regardless which y coordinate it has

        :param event: data of the mouse clicked event
        :param plane: coordinates as tuples (x, y)
        :return: index or none
        """

        if event is None:
            return None

        if not plane:
            return None

        xt = [i[1] for i in plane]
        index = int(bisect.bisect_left(xt, event.xdata))

        return index

    @staticmethod
    def writeRetrofitData(mountModel, buildModel):
        """

        :param mountModel:
        :param buildModel:
        :return:
        """

        for i, mPoint in enumerate(buildModel):
            mPoint['errorRMS'] = mountModel.starList[i].errorRMS
            mPoint['errorAngle'] = mountModel.starList[i].errorAngle.degrees
            mPoint['haMountModel'] = mountModel.starList[i].coord.ra.hours
            mPoint['decMountModel'] = mountModel.starList[i].coord.dec.degrees
            mPoint['errorRA'] = mountModel.starList[i].errorRA()
            mPoint['errorDEC'] = mountModel.starList[i].errorDEC()
            mPoint['errorIndex'] = mountModel.starList[i].number
            mPoint['modelTerms'] = mountModel.terms
            mPoint['modelErrorRMS'] = mountModel.errorRMS
            mPoint['modelOrthoError'] = mountModel.orthoError.degrees * 3600
            mPoint['modelPolarError'] = mountModel.polarError.degrees * 3600

        return buildModel
