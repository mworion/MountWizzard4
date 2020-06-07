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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import
from mw4.gui import widget
from mw4.gui.widgets import mount3D_ui


class Mount3DWindow(widget.MWidget):
    """
    the Mount3DWindow window class handles

    """

    # length of forecast time in hours
    FORECAST_TIME = 3
    # earth radius
    EARTH_RADIUS = 6378.0

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool

        self.ui = mount3D_ui.Ui_Mount3DDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.mount3d = self.embedMatplot(self.ui.mount3d, constrainedLayout=False)
        self.mount3d.parentWidget().setStyleSheet(self.BACK_BG)
        self.mountTop = self.embedMatplot(self.ui.mountTop, constrainedLayout=False)
        self.mountTop.parentWidget().setStyleSheet(self.BACK_BG)
        self.mountX = self.embedMatplot(self.ui.mountX, constrainedLayout=False)
        self.mountX.parentWidget().setStyleSheet(self.BACK_BG)
        self.mountY = self.embedMatplot(self.ui.mountY, constrainedLayout=False)
        self.mountY.parentWidget().setStyleSheet(self.BACK_BG)

        # self.app.mount.signals.locationDone.connect(self.drawMount)
        self.app.update1s.connect(self.drawMount)

        self.initConfig()
        self.showWindow()

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        if 'mount3DW' not in self.app.config:
            self.app.config['mount3DW'] = {}
        config = self.app.config['mount3DW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        if 'mount3DW' not in self.app.config:
            self.app.config['mount3DW'] = {}
        config = self.app.config['mount3DW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()

        return True

    def closeEvent(self, closeEvent):
        """
        closeEvent is overloaded to be able to store the data before the windows is close
        and all it's data is garbage collected

        :param closeEvent:
        :return:
        """
        self.storeConfig()

        # gui signals
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        showWindow starts constructing the main window for satellite view and shows the
        window content

        :return: True for test purpose
        """
        self.show()

        return True

    def drawMount(self):
        """
        :return: success
        """

        figures = [self.mountTop.figure,
                   self.mountX.figure,
                   self.mountY.figure,
                   self.mount3d.figure]
        axes = []

        for fig in figures:
            fig.clf()
            fig.subplots_adjust(left=-0.1, right=1.1, bottom=-0.3, top=1.2)
            axes.append(fig.add_subplot(111, projection='3d'))

        for axe in axes:
            axe.axes.set_xlim3d(left=-1, right=1)
            axe.axes.set_ylim3d(bottom=-1, top=1)
            axe.axes.set_zlim3d(bottom=0, top=2)
            axe.set_facecolor((0, 0, 0, 0))
            axe.tick_params(colors=self.M_GREY, labelsize=12)
            # axe.set_axis_off()
            # axe.grid(color=self.M_BLUE, alpha=0.5, linestyle='.', lw=1)
            axe.xaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
            axe.yaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))
            axe.zaxis.set_pane_color((0.0, 0.0, 0.0, 0.0))

            axe.w_xaxis.line.set_color(self.M_BLUE)
            axe.w_yaxis.line.set_color(self.M_BLUE)
            axe.w_zaxis.line.set_color(self.M_BLUE)

            axe.w_xaxis.gridlines.set_color(self.M_BLUE)
            axe.w_yaxis.gridlines.set_color(self.M_BLUE)
            axe.w_zaxis.gridlines.set_color(self.M_BLUE)
            axe.w_xaxis.gridlines.set_lw(1)
            axe.w_yaxis.gridlines.set_lw(1)
            axe.w_zaxis.gridlines.set_lw(1)
            axe.w_xaxis.gridlines.set_alpha(0.5)
            axe.w_yaxis.gridlines.set_alpha(0.5)
            axe.w_zaxis.gridlines.set_alpha(0.5)
            axe.w_xaxis.gridlines.set_linestyle(':')
            axe.w_yaxis.gridlines.set_linestyle(':')
            axe.w_zaxis.gridlines.set_linestyle(':')

            axe.set_xlabel('X direction', color=self.M_BLUE)
            axe.set_ylabel('Y direction', color=self.M_BLUE)
            axe.set_zlabel('Z direction', color=self.M_BLUE)

        # top view
        axes[0].view_init(90, 180)

        # side view X
        axes[1].view_init(0, 180)

        # side view Y
        axes[2].view_init(0, 90)

        # iso view
        axes[3].view_init(30, 210)

        # getting information from mount and draw it
        mount = self.app.mount
        ha = mount.obsSite.haJNow
        dec = mount.obsSite.decJNow
        pierside = mount.obsSite.pierside
        lat = mount.obsSite.location.latitude

        # initializing the mount
        mount.geometry.initializeGeometry('10micron GM1000HPS')

        # setting values
        mount.geometry.domeRadius = 1.5
        mount.geometry.offNorth = 0
        mount.geometry.offEast = 0.01
        mount.geometry.offVert = 0.08
        mount.geometry.offLAT = 0.15
        mount.geometry.offGEM = 0.42

        alt, az = mount.geometry.calcTransformationMatrices(ha=ha,
                                                            dec=dec,
                                                            lat=lat,
                                                            pierside=pierside)

        points = mount.geometry.transVector

        if points is None:
            return

        for axe in axes:
            # base point
            p0 = points[0]
            axe.plot([p0[0]],
                     [p0[1]],
                     [p0[2]],
                     marker='o', markersize=5, color=self.M_RED)

            # offsets north east vertical
            p1 = points[1]
            axe.plot([p0[0], p1[0]],
                     [p0[1], p1[1]],
                     [p0[2], p1[2]],
                     lw=1, color=self.M_GREY)
            axe.plot([p1[0]],
                     [p1[1]],
                     [p1[2]],
                     marker='o', markersize=1, color=self.M_GREY)

            # offsets to turning point azimuth
            p2 = points[2]
            axe.plot([p1[0], p2[0]],
                     [p1[1], p2[1]],
                     [p1[2], p2[2]],
                     lw=1, color=self.M_GREY)
            axe.plot([p2[0]],
                     [p2[1]],
                     [p2[2]],
                     marker='o', markersize=1, color=self.M_GREY)

            # offsets to lat compensation
            p3 = points[3]
            axe.plot([p2[0], p3[0]],
                     [p2[1], p3[1]],
                     [p2[2], p3[2]],
                     lw=1, color=self.M_GREY)
            axe.plot([p3[0]],
                     [p3[1]],
                     [p3[2]],
                     marker='o', markersize=5, color=self.M_YELLOW)

            # offsets to GEM point
            p4 = points[4]
            axe.plot([p3[0], p4[0]],
                     [p3[1], p4[1]],
                     [p3[2], p4[2]],
                     lw=1, color=self.M_GREY)
            axe.plot([p4[0]],
                     [p4[1]],
                     [p4[2]],
                     marker='o', markersize=1, color=self.M_GREY)

            # offsets
            p5 = points[5]
            axe.plot([p4[0], p5[0]],
                     [p4[1], p5[1]],
                     [p4[2], p5[2]],
                     lw=1, color=self.M_GREY)
            axe.plot([p5[0]],
                     [p5[1]],
                     [p5[2]],
                     marker='o', markersize=5, color=self.M_GREEN)

            # offsets
            p6 = points[6]
            axe.plot([p5[0], p6[0]],
                     [p5[1], p6[1]],
                     [p5[2], p6[2]],
                     lw=1, color=self.M_GREY)
            axe.plot([p6[0]],
                     [p6[1]],
                     [p6[2]],
                     marker='o', markersize=1, color=self.M_BLUE)

            # offsets to GEM point
            p7 = points[7]
            axe.plot([p6[0], p7[0]],
                     [p6[1], p7[1]],
                     [p6[2], p7[2]],
                     lw=1, color=self.M_GREY)
            axe.plot([p7[0]],
                     [p7[1]],
                     [p7[2]],
                     marker='o', markersize=1, color=self.M_GREY)

            # offsets from GEM to OTA
            p8 = points[8]
            axe.plot([p7[0], p8[0]],
                     [p7[1], p8[1]],
                     [p7[2], p8[2]],
                     lw=1, color=self.M_GREY)
            axe.plot([p8[0]],
                     [p8[1]],
                     [p8[2]],
                     marker='o', markersize=3, color=self.M_RED)

            # offsets from OTA LAT
            p9 = points[9]
            axe.plot([p8[0], p9[0]],
                     [p8[1], p9[1]],
                     [p8[2], p9[2]],
                     lw=3, color=self.M_GREEN)
            axe.plot([p9[0]],
                     [p9[1]],
                     [p9[2]],
                     marker='o', markersize=3, color=self.M_BLUE)

            # offsets from OTA to sky
            p10 = points[10]
            axe.plot([p9[0], p10[0]],
                     [p9[1], p10[1]],
                     [p9[2], p10[2]],
                     lw=3, color=self.M_GREEN)
            axe.plot([p10[0]],
                     [p10[1]],
                     [p10[2]],
                     marker='o', markersize=3, color=self.M_RED)

            axe.figure.canvas.draw()

        return True
