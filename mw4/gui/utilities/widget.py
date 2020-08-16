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

# external packages
import numpy as np
import PyQt5.QtWidgets
import PyQt5.QtGui
import PyQt5.QtCore
import PyQt5.uic
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# local imports
from base.loggerMW import CustomLogger
from gui.utilities import styles

__all__ = [
    'MWidget',
]


class FileSortProxyModel(PyQt5.QtCore.QSortFilterProxyModel):
    """
    FileSortProxyModel enables a proxy solution for reversing the order of all file dialogues.
    The sorting is now Descending meaning the last added files will be on top.
    This is don by just overwriting the sort method
    """

    def sort(self, column, order):
        self.sourceModel().sort(0, PyQt5.QtCore.Qt.DescendingOrder)


class MWidget(PyQt5.QtWidgets.QWidget, styles.MWStyles):
    """
    MWidget defines the common parts for all windows used in MountWizzard 4. namely the
    sizes and the styles. styles are defined separately in a css looking stylesheet.
    standard screen size will be 800x600 pixel
    """

    __all__ = ['MWidget',
               ]

    logger = logging.getLogger(__name__)
    log = CustomLogger(logger, {})

    def __init__(self):
        super().__init__()

        self.palette = PyQt5.QtGui.QPalette()
        self.initUI()
        self.screenSizeX = PyQt5.QtWidgets.QDesktopWidget().screenGeometry().width()
        self.screenSizeY = PyQt5.QtWidgets.QDesktopWidget().screenGeometry().height()
        self.setAttribute(PyQt5.QtCore.Qt.WA_DeleteOnClose, True)

    def closeEvent(self, closeEvent):
        super().closeEvent(closeEvent)

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

        if not isinstance(icon, PyQt5.QtGui.QIcon):
            iconset = PyQt5.QtWidgets.qApp.style().standardIcon(icon)
            icon = PyQt5.QtGui.QIcon(iconset)

        gui.setIcon(icon)
        gui.setProperty('iconset', True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)
        gui.setIconSize(PyQt5.QtCore.QSize(16, 16))
        return True

    def getStyle(self):
        """
        getStyle return the actual stylesheet for the used platform

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
        self.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))

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
    def embedMatplot(widget=None, constrainedLayout=True):
        """
        IntMatplotlib provides the wrapper to use matplotlib drawings inside a pyqt5
        application gui. you call it with the parent widget, which is linked to matplotlib
        canvas of the same size. the background is set to transparent, so you could layer
        multiple figures on top.

        :param      widget:             parent ui element, which is the reference for embedding
        :param      constrainedLayout:
        :return:    staticCanvas:   matplotlib reference as parent for figures
        """

        if not widget:
            return None

        # to avoid a white flash before drawing on top.
        widget.setStyleSheet("background:transparent;")
        layout = PyQt5.QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        staticCanvas = FigureCanvas(Figure(dpi=75,
                                           facecolor='none',
                                           frameon=False,
                                           constrained_layout=constrainedLayout,
                                           )
                                    )
        FigureCanvasQTAgg.updateGeometry(staticCanvas)
        layout.addWidget(staticCanvas)
        staticCanvas.setParent(widget)
        return staticCanvas

    @staticmethod
    def extractNames(names=''):
        """
        extractName splits a given path to basename and extension
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

    def prepareFileDialog(self, window=None, enableDir=False):
        """
        prepareFileDialog does some preparations for geometry and general settings

        :param window:  parent class
        :param enableDir:   allows dir selection in file box
        :return:        dlg, the dialog widget
        """

        if not window:
            return None

        dlg = PyQt5.QtWidgets.QFileDialog()
        dlg.setOptions(PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog)
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))
        dlg.setStyleSheet(self.getStyle())
        dlg.setViewMode(PyQt5.QtWidgets.QFileDialog.List)
        dlg.setModal(True)
        dlg.setProxyModel(FileSortProxyModel(self))

        if enableDir:
            dlg.setFilter(PyQt5.QtCore.QDir.Files | PyQt5.QtCore.QDir.AllDirs)
        else:
            dlg.setFilter(PyQt5.QtCore.QDir.Files)

        # remove unnecessary widgets from the file selector box
        # dlg.findChildren(PyQt5.QtWidgets.QListView, 'sidebar')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QComboBox, 'lookInCombo')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QLabel, 'lookInLabel')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'backButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'forwardButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'toParentButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'newFolderButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'listModeButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'detailModeButton')[0].setVisible(False)

        # position the window to parent in the center
        width = 500
        height = 400
        ph = window.geometry().height()
        pw = window.geometry().width()
        px = window.geometry().x()
        py = window.geometry().y()
        dlg.setGeometry(px + int(0.5 * (pw - width)),
                        py + int(0.5 * (ph - height)),
                        width, height)
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
                 multiple=False):
        """
        openFile handles a single file select with filter in a non native format.

        :param window:      parent window class
        :param title:       title for the file dialog
        :param folder:      starting folder for searching the file
        :param filterSet:   file extension filter
        :param enableDir:   allows dir selection in file box
        :param multiple :   allows multiple selection in file box
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

        dlg = self.prepareFileDialog(window=window, enableDir=enableDir)
        dlg.setAcceptMode(PyQt5.QtWidgets.QFileDialog.AcceptOpen)

        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(folder)
        if multiple:
            dlg.setFileMode(PyQt5.QtWidgets.QFileDialog.ExistingFiles)
        else:
            dlg.setFileMode(PyQt5.QtWidgets.QFileDialog.ExistingFile)

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
        dlg.setAcceptMode(PyQt5.QtWidgets.QFileDialog.AcceptSave)

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
        dlg.setAcceptMode(PyQt5.QtWidgets.QFileDialog.AcceptOpen)

        dlg.setWindowTitle(title)
        dlg.setDirectory(folder)
        dlg.setFileMode(PyQt5.QtWidgets.QFileDialog.DirectoryOnly)

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

        class Filter(PyQt5.QtCore.QObject):
            clicked = PyQt5.QtCore.pyqtSignal(object)

            def eventFilter(self, obj, event):
                if obj == widget:
                    if event.type() == PyQt5.QtCore.QEvent.MouseButtonRelease:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit(widget)
                            return True
                return False

        _filter = Filter(widget)
        widget.installEventFilter(_filter)
        return _filter.clicked

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

    def generatePolar(self, widget=None, title=''):
        """

        :param widget:
        :param title:
        :return:
        """

        if widget is None:
            return None, None
        if not hasattr(widget, 'figure'):
            return None, None

        fig = widget.figure
        fig.clf()
        axe = fig.add_subplot(1,
                              1,
                              1,
                              polar=True,
                              facecolor=self.M_GREY_DARK)
        axe.grid(True,
                 color=self.M_GREY,
                 )

        if title:
            axe.set_title(title,
                          color=self.M_BLUE,
                          fontweight='bold',
                          pad=15,
                          )

        axe.tick_params(axis='x',
                        colors=self.M_BLUE,
                        labelsize=12,
                        )
        axe.tick_params(axis='y',
                        colors=self.M_BLUE,
                        labelsize=12,
                        )
        axe.set_theta_zero_location('N')
        axe.set_rlabel_position(45)
        axe.set_theta_direction(-1)
        # ticks have to be set before labels to be sure to have them positioned correctly
        axe.set_xticks(np.radians([0, 45, 90, 135, 180, 225, 270, 315]))
        axe.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

        return axe, fig

    def generateFlat(self, widget=None, title=''):
        """

        :param widget:
        :param title:
        :return:
        """

        if widget is None:
            return None, None
        if not hasattr(widget, 'figure'):
            return None, None

        figure = widget.figure
        figure.clf()
        axe = figure.add_subplot(1, 1, 1, facecolor=self.M_GREY_DARK)

        axe.spines['bottom'].set_color(self.M_BLUE)
        axe.spines['top'].set_color(self.M_BLUE)
        axe.spines['left'].set_color(self.M_BLUE)
        axe.spines['right'].set_color(self.M_BLUE)
        axe.grid(True, color=self.M_GREY)

        if title:
            axe.set_title(title,
                          color=self.M_BLUE,
                          fontweight='bold',
                          pad=15,
                          )

        axe.tick_params(axis='x',
                        colors=self.M_BLUE,
                        labelsize=12)
        axe.tick_params(axis='y',
                        colors=self.M_BLUE,
                        labelsize=12)

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
