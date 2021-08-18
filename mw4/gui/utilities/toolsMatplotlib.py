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
import logging
import bisect

# external packages
import numpy as np
from PyQt5.QtWidgets import QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

# local imports

__all__ = [
    'ToolsMatplotlib',
]


class ToolsMatplotlib:
    """
    """

    __all__ = ['ToolsMatplotlib',
               ]

    log = logging.getLogger(__name__)

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

    @staticmethod
    def embedMatplot(widget=None, constrainedLayout=True):
        """
        embedMatplot provides the wrapper to use matplotlib drawings inside a
        pyqt5 application gui. you call it with the parent widget, which is
        linked to matplotlib canvas of the same size. the background is set to
        transparent, so you could layer multiple figures on top.

        :param   widget: parent ui element, which is the reference for embedding
        :param   constrainedLayout:
        :return: staticCanvas:   matplotlib reference as parent for figures
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

    def generatePolar(self, widget=None, title='', horizon=False,
                      showAxes=True, reverse=False):
        """
        :param widget:
        :param title:
        :param horizon:
        :param showAxes:
        :param reverse: does change E/W setting
        :return:
        """
        if widget is None:
            return None, None
        if not hasattr(widget, 'figure'):
            return None, None

        if showAxes:
            color = self.M_BLUE
            colorGrid = self.M_GREY

        else:
            color = self.M_TRANS
            colorGrid = self.M_TRANS

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
        axe.spines['polar'].set_color(color)

        if reverse:
            axe.set_theta_direction(1)
        else:
            axe.set_theta_direction(-1)

        axe.set_xticks(np.radians([0, 45, 90, 135, 180, 225, 270, 315]))
        axe.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

        if not horizon:
            return axe, figure

        axe.set_ylim(0, 90)
        axe.set_yticks(range(0, 90, 10))
        axe.set_yticklabels(['', '80', '70', '60', '50', '40', '30', '20', '10'])
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

        if showAxes:
            color = self.M_BLUE
        else:
            color = self.M_TRANS

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

        if showAxes:
            axe.grid(showAxes, color=self.M_GREY)
        else:
            axe.grid(showAxes)

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
        axe.set_xticklabels(['0 N', '45 NE', '90 E', '135 SE', '180 S',
                             '225 SW', '270 W', '315 NW', '360 N'])
        axe.set_xlabel('Azimuth [degrees]', color=color, fontweight='bold',
                       fontsize=12)
        axe.set_ylabel('Altitude [degrees]', color=color, fontweight='bold',
                       fontsize=12)

        return axe, figure

    def generateColorbar(self, figure=None, scatter=None, label=''):
        """
        :param figure:
        :param scatter:
        :param label:
        :return:
        """
        if len(figure.axes) > 1:
            return False

        formatString = FormatStrFormatter('%1.0f')
        figure.colorbar(scatter,
                        pad=0.1,
                        fraction=0.12,
                        aspect=25,
                        shrink=0.9,
                        format=formatString,
                        )
        figure.axes[1].set_ylabel(label, color=self.M_BLUE)
        figure.axes[1].tick_params(axis='y', labelcolor=self.M_BLUE,
                                   color=self.M_BLUE)

        return True

    @staticmethod
    def getIndexPoint(event=None, plane=None, epsilon=2):
        """
        getIndexPoint returns the index of the point which is nearest to the
        coordinate of the mouse click when the click is in distance epsilon of
        the points. otherwise
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
    def getIndexPointX(x=None, plane=None):
        """
        getIndexPointX returns the index of the point which has a x coordinate
        closest to the left of the x coordinate of the mouse click regardless
        which y coordinate it has

        :param x: data of the mouse clicked event
        :param plane: coordinates as tuples (x, y)
        :return: index or none
        """
        if x is None:
            return None
        if not plane:
            return None

        xt = [i[1] for i in plane]
        index = int(bisect.bisect_left(xt, x))
        return index
