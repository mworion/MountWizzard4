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
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import platform
# external packages
import PyQt5.QtWidgets
import PyQt5.QtGui
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot
import matplotlib.backends.backend_qt5agg as backend
# local imports
import base.styles
import base.tpool


version = '0.1'
__all__ = [
    'MWidget',
    'IntMatplotlib',
]


class MWidget(PyQt5.QtWidgets.QWidget, base.styles.MWStyles):
    """
    MWidget defines the common parts for all windows used in MountWizzard 4. namely the
    sizes and the styles. styles are defined separately in a css looking stylesheet.
    standard screen size will be 800x600 pixel
    """

    logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()
        self.palette = PyQt5.QtGui.QPalette()
        self.initUI()
        self.screenSizeX = PyQt5.QtWidgets.QDesktopWidget().screenGeometry().width()
        self.screenSizeY = PyQt5.QtWidgets.QDesktopWidget().screenGeometry().height()
        self.showStatus = False

    def closeEvent(self, closeEvent):
        self.showStatus = False
        self.hide()

    @staticmethod
    def wIcon(gui, icon):
        """
        widget icon adds an icon to a gui element like an button.

        :param      gui:        gui element, which will be expanded by an icon
        :param      icon:       icon to be added
        :return:    nothing
        """

        iconset = PyQt5.QtWidgets.qApp.style().standardIcon(icon)
        gui.setIcon(PyQt5.QtGui.QIcon(iconset))
        gui.setProperty('iconset', True)
        gui.style().unpolish(gui)
        gui.style().polish(gui)
        gui.setIconSize(PyQt5.QtCore.QSize(16, 16))

    def initUI(self):
        """
        init_UI makes the basic initialisation of the GUI. is sets the window flags
        and sets the handling of the window. is as well fixes the windows size (unless
        a windows will be scalable later on. in addition the appropriate style sheet
        for mac and non mac will be selected and used.

        :return:    nothing
        """

        self.setWindowFlags((self.windowFlags()
                             | PyQt5.QtCore.Qt.CustomizeWindowHint)
                            & ~PyQt5.QtCore.Qt.WindowMaximizeButtonHint)
        self.setMouseTracking(True)
        # sizing in gui should be fixed, because I have a static layout
        self.setFixedSize(800, 600)
        self.setWindowIcon(PyQt5.QtGui.QIcon(':/mw4.ico'))
        if platform.system() == 'Darwin':
            self.setStyleSheet(self.MAC_STYLE + self.BASIC_STYLE)
        else:
            self.setStyleSheet(self.NON_MAC_STYLE + self.BASIC_STYLE)

    @staticmethod
    def changeStylesheet(ui, item, value):
        """
        changeStylesheet changes the stylesheet of a given uii element and makes it
        visible. therefore the element has to be unpolished and polished again.

        :param      ui:     ui element, where the stylesheet has to be changed
        :param      item:   stylesheet attribute which has to be changes
        :param      value:  new value of the attribute
        :return:
        """

        ui.style().unpolish(ui)
        ui.setProperty(item, value)
        ui.style().polish(ui)

    @staticmethod
    def clearPolar(wid):
        """
        clearPolar clears and setups the canvas widget for drawing. it sets the labels, ticks
        and some other ui styles.

        :param      wid:    matplotlib canvas widget for drawing
        :return:    wid     modified widget
        """

        wid.fig.clf()
        wid.axes = wid.fig.add_subplot(1,
                                       1,
                                       1,
                                       polar=True)
        wid.axes.grid(True,
                      color='#404040',
                      )
        wid.axes.set_title('Actual Mount Model',
                           color='white',
                           fontweight='bold',
                           pad=15,
                           )
        wid.fig.subplots_adjust(left=0.07,
                                right=1,
                                bottom=0.03,
                                top=0.97,
                                )
        wid.axes.set_facecolor((32 / 256, 32 / 256, 32 / 256))
        wid.axes.tick_params(axis='x',
                             colors='#2090C0',
                             labelsize=12,
                             )
        wid.axes.tick_params(axis='y',
                             colors='#2090C0',
                             labelsize=12,
                             )
        wid.axes.set_theta_zero_location('N')
        wid.axes.set_theta_direction(-1)
        wid.axes.set_yticks(range(0, 90, 10))
        yLabel = ['', '', '', '', '', '', '', '', '', '']
        wid.axes.set_yticklabels(yLabel,
                                 color='#2090C0',
                                 fontweight='bold')
        wid.axes.set_rlabel_position(45)
        return wid

    def integrateMatplotlib(ui):
        """
        IntMatplotlib provides the wrapper to use matplotlib drawings inside a pyqt5 application
        gui. you call it with the parent widget, which is linked to matplotlib canvas of the same
        size. the background is set to transparent, so you could layer multiple figures on top.

        """

        # to avoid a white flash before drawing on top.
        ui.setStyleSheet("background:transparent;")
        layout = PyQt5.QtWidgets.QVBoxLayout(ui)
        layout.setContentsMargins(0, 0, 0, 0)
        staticCanvas = matplotlib.figure.Figure(dpi=75,
                                                facecolor=(25 / 256,
                                                           25 / 256,
                                                           25 / 256,))
        backend.FigureCanvasQTAgg.setSizePolicy(staticCanvas,
                                                PyQt5.QtWidgets.QSizePolicy.Expanding,
                                                PyQt5.QtWidgets.QSizePolicy.Expanding
                                                )
        backend.FigureCanvasQTAgg.updateGeometry(staticCanvas)
        layout.addWidget(staticCanvas)
        return ui


class IntMatplotlib(backend.FigureCanvasQTAgg):
    """
    IntMatplotlib provides the wrapper to use matplotlib drawings inside a pyqt5 application
    gui. you call it with the parent widget, which is linked to matplotlib canvas of the same
    size. the background is set to transparent, so you could layer multiple figures on top.

    """

    def __init__(self, parent=None):
        # to avoid a white flash before drawing on top.
        parent.setStyleSheet("background:transparent;")
        helper = PyQt5.QtWidgets.QVBoxLayout(parent)
        helper.setContentsMargins(0, 0, 0, 0)
        self.fig = matplotlib.figure.Figure(dpi=75,
                                            facecolor=(25 / 256,
                                                       25 / 256,
                                                       25 / 256,))
        backend.FigureCanvasQTAgg.__init__(self, self.fig)
        backend.FigureCanvasQTAgg.setSizePolicy(self,
                                                PyQt5.QtWidgets.QSizePolicy.Expanding,
                                                PyQt5.QtWidgets.QSizePolicy.Expanding
                                                )
        backend.FigureCanvasQTAgg.updateGeometry(self)
        helper.addWidget(self)
