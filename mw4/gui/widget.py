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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform
import os
# external packages
import PyQt5.QtWidgets
import PyQt5.QtGui
import PyQt5.QtCore
import PyQt5.uic
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# local imports
from . import styles

version = '0.1'
__all__ = [
    'MWidget',
]


class MWidget(PyQt5.QtWidgets.QWidget, styles.MWStyles):
    """
    MWidget defines the common parts for all windows used in MountWizzard 4. namely the
    sizes and the styles. styles are defined separately in a css looking stylesheet.
    standard screen size will be 800x600 pixel
    """

    __all__ = ['closeEvent',
               'wIcon',
               'initUI',
               'changeStyleSheet',
               'clearPolar',
               'integrateMatplotlib',
               ]

    version = '0.5'
    logger = logging.getLogger(__name__)

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
    def wIcon(gui, icon):
        """
        widget icon adds an icon to a gui element like an button.

        :param      gui:        gui element, which will be expanded by an icon
        :param      icon:       icon to be added
        :return:    true for test purpose
        """

        iconset = PyQt5.QtWidgets.qApp.style().standardIcon(icon)
        gui.setIcon(PyQt5.QtGui.QIcon(iconset))
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
    def changeStyleDynamic(ui, item, value):
        """
        changeStyleDynamic changes the stylesheet of a given uii element and makes it
        visible. therefore the element has to be unpolished and polished again.

        :param      ui:     ui element, where the stylesheet has to be changed
        :param      item:   stylesheet attribute which has to be changes
        :param      value:  new value of the attribute
        :return:    true for test purpose
        """

        ui.style().unpolish(ui)
        ui.setProperty(item, value)
        ui.style().polish(ui)

        return True

    @staticmethod
    def clearPolar(widget):
        """
        clearPolar clears and setups the canvas widget for drawing. it sets the labels,
        ticks and some other ui styles.

        :param      widget:    matplotlib canvas widget for drawing
        :return:    fig        figure in widget
        :return:    axes       axes in figure
        """

        fig = widget.figure
        fig.clf()
        axes = fig.add_subplot(1,
                               1,
                               1,
                               polar=True,
                               facecolor='none')
        axes.grid(True,
                  color='#404040',
                  )
        axes.set_title('Actual Mount Model',
                       color='white',
                       fontweight='bold',
                       pad=15,
                       )
        fig.subplots_adjust(left=0.07,
                            right=1,
                            bottom=0.03,
                            top=0.97,
                            )
        axes.set_facecolor((32 / 256, 32 / 256, 32 / 256))
        axes.tick_params(axis='x',
                         colors='#2090C0',
                         labelsize=12,
                         )
        axes.tick_params(axis='y',
                         colors='#2090C0',
                         labelsize=12,
                         )
        axes.set_theta_zero_location('N')
        axes.set_theta_direction(-1)
        axes.set_yticks(range(0, 90, 10))
        yLabel = ['', '', '', '', '', '', '', '', '', '']
        axes.set_yticklabels(yLabel,
                             color='#2090C0',
                             fontweight='bold')
        axes.set_rlabel_position(45)
        return fig, axes

    @staticmethod
    def embedMatplot(ui):
        """
        IntMatplotlib provides the wrapper to use matplotlib drawings inside a pyqt5
        application gui. you call it with the parent widget, which is linked to matplotlib
        canvas of the same size. the background is set to transparent, so you could layer
        multiple figures on top.

        :param      ui:             parent ui element, which is the reference for embedding
        :return:    staticCanvas:   matplotlib reference as parent for figures
        """

        # to avoid a white flash before drawing on top.
        ui.setStyleSheet("background:transparent;")
        layout = PyQt5.QtWidgets.QVBoxLayout(ui)
        layout.setContentsMargins(0, 0, 0, 0)
        staticCanvas = FigureCanvas(Figure(dpi=75,
                                           facecolor='none',
                                           frameon=False,
                                           )
                                    )
        FigureCanvasQTAgg.updateGeometry(staticCanvas)
        layout.addWidget(staticCanvas)
        staticCanvas.setParent(ui)
        return staticCanvas

    @staticmethod
    def extractNames(names):
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
            shortList.append(short)
            nameList.append(name)
            extList.append(ext)

        if len(names) == 1:
            return name, short, ext
        else:
            return nameList, shortList, extList

    def prepareFileDialog(self, window, enableDir):
        """
        prepareFileDialog does some preparations for geometry and general settings

        :param window:  parent class
        :param enableDir:   allows dir selection in file box
        :return:        dlg, the dialog widget
        """

        dlg = PyQt5.QtWidgets.QFileDialog()
        dlg.setOptions(PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog)
        dlg.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))
        dlg.setStyleSheet(self.getStyle())
        dlg.setViewMode(PyQt5.QtWidgets.QFileDialog.List)
        dlg.setModal(True)

        if enableDir:
            dlg.setFilter(PyQt5.QtCore.QDir.Files | PyQt5.QtCore.QDir.AllDirs)
        else:
            dlg.setFilter(PyQt5.QtCore.QDir.Files)

        # remove unnecessary widgets from the file selector box
        dlg.findChildren(PyQt5.QtWidgets.QListView, 'sidebar')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QComboBox, 'lookInCombo')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QLabel, 'lookInLabel')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'backButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'forwardButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'toParentButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'newFolderButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'listModeButton')[0].setVisible(False)
        dlg.findChildren(PyQt5.QtWidgets.QWidget, 'detailModeButton')[0].setVisible(False)

        # position the window to parent in the center
        width = 400
        height = 400
        ph = window.geometry().height()
        pw = window.geometry().width()
        px = window.geometry().x()
        py = window.geometry().y()
        dlg.setGeometry(px + 0.5 * (pw - width), py + 0.5 * (ph - height), 400, 400)
        return dlg

    def openFile(self, window, title, folder, filterSet, enableDir=False, multiple=False):
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

        dlg = self.prepareFileDialog(window, enableDir)
        dlg.setAcceptMode(PyQt5.QtWidgets.QFileDialog.AcceptOpen)

        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(folder)
        if multiple:
            dlg.setFileMode(PyQt5.QtWidgets.QFileDialog.ExistingFiles)
        else:
            dlg.setFileMode(PyQt5.QtWidgets.QFileDialog.ExistingFile)

        dlg.exec_()
        filePath = dlg.selectedFiles()
        full, short, ext = self.extractNames(filePath)
        return full, short, ext

    def saveFile(self, window, title, folder, filterSet, enableDir=False):
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

        dlg = self.prepareFileDialog(window, enableDir)
        dlg.setAcceptMode(PyQt5.QtWidgets.QFileDialog.AcceptSave)

        dlg.setWindowTitle(title)
        dlg.setNameFilter(filterSet)
        dlg.setDirectory(folder)

        dlg.exec_()
        filePath = dlg.selectedFiles()
        full, short, ext = self.extractNames(filePath)
        return full, short, ext

    def openDir(self, window, title, folder):
        """
        openFile handles a single file select with filter in a non native format.

        :param window:      parent window class
        :param title:       title for the file dialog
        :param folder:      starting folder for searching the file
        :return:            name: full path for file else empty
                            short: just file name without extension
                            ext: extension of the file
        """

        dlg = self.prepareFileDialog(window, True)
        dlg.setAcceptMode(PyQt5.QtWidgets.QFileDialog.AcceptOpen)

        dlg.setWindowTitle(title)
        dlg.setDirectory(folder)
        dlg.setFileMode(PyQt5.QtWidgets.QFileDialog.DirectoryOnly)

        dlg.exec_()
        filePath = dlg.selectedFiles()
        full, short, ext = self.extractNames(filePath)
        return full, short, ext

    @staticmethod
    def clickable(widget):
        """
        It uses one filter object per label, which is created when the clickable()
        function is called with the widget that is to be click-enabled. The function
        returns a clicked() signal that actually belongs to the filter object. The caller
        can connect this signal to a suitable callable object.

        :param widget:      widget for what the event filter works
        :return:            filtered event
        """

        class Filter(PyQt5.QtCore.QObject):
            clicked = PyQt5.QtCore.pyqtSignal()

            def eventFilter(self, obj, event):
                if obj == widget:
                    if event.type() == PyQt5.QtCore.QEvent.MouseButtonRelease:
                        if obj.rect().contains(event.pos()):
                            self.clicked.emit()
                            return True
                return False

        _filter = Filter(widget)
        widget.installEventFilter(_filter)
        return _filter.clicked
