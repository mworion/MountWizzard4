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
import bisect

# external packages
import PyQt5
import numpy as np
import matplotlib.path as mpath

# local import


class HemisphereWindowExt(object):
    """
    the HemisphereWindowExt window class handles

    """

    __all__ = ['HemisphereWindowExt',
               ]

    @staticmethod
    def markerPoint():
        """
        markerPoint constructs a custom marker for presentation of modeldata points by
        concatenating the circle with an internal cutout of the star

        :return: marker
        """

        circleB = mpath.Path.unit_circle()
        circleS = mpath.Path.unit_circle()
        verts = np.concatenate([circleB.vertices, 0.5 * circleS.vertices])
        codes = np.concatenate([circleB.codes, circleS.codes])
        marker = mpath.Path(verts, codes)

        return marker

    @staticmethod
    def markerAltAz():
        """
        markerAltAz constructs a custom marker for AltAz pointer by
        concatenating the circle with an internal cutout of the star

        :return: marker
        """

        circleB = mpath.Path.unit_circle()
        circleM = mpath.Path.unit_circle()
        circleS = mpath.Path.unit_circle()
        verts = np.concatenate([circleB.vertices,
                                0.8 * circleM.vertices,
                                0.3 * circleS.vertices])
        codes = np.concatenate([circleB.codes,
                                circleM.codes,
                                circleS.codes])
        marker = mpath.Path(verts, codes)

        return marker

    @staticmethod
    def markerStar():
        """
        markerStar constructs a custom marker for presentation of modeldata points by
        concatenating the circle with an internal cutout of the star

        :return: marker
        """

        star = mpath.Path.unit_regular_star(8)
        verts = np.concatenate([star.vertices])
        codes = np.concatenate([star.codes])
        marker = mpath.Path(verts, codes)

        return marker

    def configOperationMode(self):
        """
        configOperationMode enables and disables the select PolarAlign button according
        to the status of Show align stars. without showing align stars it does not make
        sense to enable this function.

        :return: nothing
        """

        if self.ui.checkShowAlignStar.isChecked():
            self.ui.checkPolarAlignment.setEnabled(True)
        else:
            self.ui.checkPolarAlignment.setEnabled(False)
            if self.ui.checkPolarAlignment.isChecked():
                self.ui.checkEditNone.setChecked(True)

    def setOperationMode(self):
        """
        setOperationMode changes the operation mode of the hemisphere window(s) depending
        on the choice, colors and styles will be changed.

        if we have operation mode star (polar alignment), dual axis tracking will be disabled
        and we memorize the status. in other operation modes we reconstruct the setting

        :return: success
        """

        # first time sync the status
        if self.statusDAT is None:
            self.statusDAT = self.app.mount.setting.statusDualAxisTracking

        if self.ui.checkEditNone.isChecked():
            self.operationMode = 'normal'
        elif self.ui.checkEditBuildPoints.isChecked():
            self.operationMode = 'build'
        elif self.ui.checkEditHorizonMask.isChecked():
            self.operationMode = 'horizon'
        elif self.ui.checkPolarAlignment.isChecked():
            self.operationMode = 'star'

        if self.operationMode == 'star':
            self.statusDAT = self.app.mount.setting.statusDualAxisTracking
            self.app.mount.setting.setDualAxisTracking(False)
            self.changeStyleDynamic(self.app.mainW.ui.statusDualAxisTracking,
                                    'color',
                                    'yellow')
        else:
            self.app.mount.setting.setDualAxisTracking(self.statusDAT)
            self.changeStyleDynamic(self.app.mainW.ui.statusDualAxisTracking,
                                    'color',
                                    '')

        self.drawHemisphere()

        return True

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
            return None

        xt = np.asarray([i[1] for i in plane])
        yt = np.asarray([i[0] for i in plane])
        d = np.sqrt((xt - event.xdata)**2 / 16 + (yt - event.ydata)**2)
        index = d.argsort()[:1][0]
        # position to far away
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
        if plane is None:
            return None
        if len(plane) < 2:
            return None

        xt = [i[1] for i in plane]
        index = int(bisect.bisect_left(xt, event.xdata) - 1)
        return index

    def showMouseCoordinates(self, event):
        """

        :param event:
        :return: success
        """

        if event.xdata is None:
            return False
        if event.ydata is None:
            return False

        self.ui.altitude.setText(f'{event.xdata:3.1f}')
        self.ui.azimuth.setText(f'{event.ydata:3.1f}')
        return True

    def onMouseNormal(self, event):
        """
        onMouseNormal handles the mouse event in normal mode. this means only a double
        click is possible and offers the opportunity to slew the telescope to a certain
        position in sky selected by the mouse.

        :param event: mouse events
        :return: success
        """

        if not event.inaxes:
            return False
        if event.button != 1 or not event.dblclick:
            return False

        azimuth = int(event.xdata + 0.5)
        altitude = int(event.ydata + 0.5)
        textFormat = 'Do you want to slew the mount to:\n\nAzimuth:\t{0}°\nAltitude:\t{1}°'

        question = textFormat.format(azimuth, altitude)
        msg = PyQt5.QtWidgets.QMessageBox
        reply = msg.question(self,
                             'Hemisphere direct slew',
                             question,
                             msg.Yes | msg.No,
                             msg.No,
                             )
        if reply != msg.Yes:
            return False
        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=altitude,
                                                    az_degrees=azimuth)
        if suc:
            self.app.dome.slewDome(altitude=altitude,
                                   azimuth=azimuth,
                                   geometry=self.app.mainW.ui.checkDomeGeometry.isChecked()
                                   )
            suc = self.app.mount.obsSite.startSlewing()
        if suc:
            self.app.message.emit('Starting slew', 0)
        else:
            self.app.message.emit('Cannot slew to: {0}, {1}'.format(azimuth, altitude), 2)
        return suc

    def addHorizonPoint(self, data=None, event=None):
        """
        addHorizonPoint calculates from the position of the left mouse click the position
        where the next horizon point should be added. the coordinates are given from mouse
        click itself.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return:
        """

        index = self.getIndexPointX(event=event, plane=data.horizonP) + 1
        suc = data.addHorizonP(value=(event.ydata, event.xdata),
                               position=index)
        return suc

    def deleteHorizonPoint(self, data=None, event=None):
        """
        deleteHorizonPoint selects the next horizon point in distance max and tries to
        delete it. there have to be at least 2 horizon point left.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return: success
        """

        index = self.getIndexPoint(event=event, plane=data.horizonP)
        suc = False
        if len(data.horizonP) > 2:
            suc = data.delHorizonP(position=index)
        return suc

    def editHorizonMask(self, data=None, event=None):
        """
        editHorizonMask does dispatching the different mouse clicks for adding or deleting
        horizon mask points and call the function accordingly.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return: success
        """

        if event.button == 1:
            suc = self.addHorizonPoint(data=data, event=event)
        elif event.button == 3:
            suc = self.deleteHorizonPoint(data=data, event=event)
        else:
            return False

        y, x = zip(*data.horizonP)
        self.horizonMarker.set_data(x, y)
        self.horizonFill.set_xy(np.column_stack((x, y)))

        self.drawHemisphere()
        return suc

    def addBuildPoint(self, data=None, event=None, axes=None):
        """
        addBuildPoint calculates from the position of the left mouse click the position
        where the next modeldata point should be added. the coordinates are given from mouse
        click itself.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :param axes: link to drawing axes in matplotlib
        :return:
        """

        if data is None:
            return False
        if event is None:
            return False

        index = self.getIndexPoint(event=event, plane=data.buildP, epsilon=360)
        # if no point found, add at the end
        if index is None:
            index = len(data.buildP)
        # take the found point closer to the end of the list
        index += 1
        suc = data.addBuildP(value=(event.ydata, event.xdata),
                             position=index)
        if not suc:
            return False

        # if succeeded, than add the data to the matplotlib hemisphere widget
        # first the point
        x = event.xdata
        y = event.ydata
        if self.ui.checkShowSlewPath.isChecked():
            ls = ':'
            lw = 1
        else:
            ls = ''
            lw = 0
        color = self.M_PINK_H
        if self.pointsBuild is None:
            newBuildP, = axes.plot(x,
                                   y,
                                   marker=self.markerPoint(),
                                   markersize=9,
                                   linestyle=ls,
                                   lw=lw,
                                   fillstyle='none',
                                   color=color,
                                   zorder=20,
                                   )
            self.pointsBuild = newBuildP

        # and than the annotation (number)
        xy = (x, y)
        newAnnotation = axes.annotate('4',
                                      xy=xy,
                                      xytext=(2, -10),
                                      textcoords='offset points',
                                      color=self.M_WHITE,
                                      zorder=10,
                                      )
        if self.pointsBuildAnnotate is None:
            self.pointsBuildAnnotate = list()
        self.pointsBuildAnnotate.insert(index, newAnnotation)
        return True

    def deleteBuildPoint(self, data=None, event=None):
        """
        deleteBuildPoint selects the next modeldata point in distance max and tries to
        delete it. there have to be at least 2 horizon point left.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return: success
        """

        index = self.getIndexPoint(event=event, plane=data.buildP)
        suc = data.delBuildP(position=index)
        if suc:
            self.pointsBuildAnnotate[index].remove()
            del self.pointsBuildAnnotate[index]
        return suc

    def editBuildPoints(self, data=None, event=None, axes=None):
        """
        editBuildPoints does dispatching the different mouse clicks for adding or deleting
        model data points and call the function accordingly.

        :param data: points in tuples (alt, az)
        :param event: mouse event
        :param axes: link to drawing axes in matplotlib
        :return: success
        """

        if event.button == 1:
            suc = self.addBuildPoint(data=data, event=event, axes=axes)
        elif event.button == 3:
            suc = self.deleteBuildPoint(data=data, event=event)
        else:
            return False

        # redraw the corrected canvas (new positions ans new numbers)
        if len(data.buildP):
            y, x = zip(*data.buildP)
        else:
            y = x = []
        self.pointsBuild.set_data(x, y)
        for i, _ in enumerate(data.buildP):
            self.pointsBuildAnnotate[i].set_text('{0:2d}'.format(i))
        self.drawHemisphere()
        return suc

    def onMouseEdit(self, event):
        """
        onMouseEdit handles the mouse event in normal mode. this means depending on the
        edit mode (horizon or model points) a left click adds a new point and right click
        deletes the selected point.

        :param event: mouse events
        :return: success
        """

        data = self.app.data
        axes = self.hemisphereMat.figure.axes[0].axes

        if not event.inaxes:
            return False
        if event.dblclick:
            return False

        if self.ui.checkEditHorizonMask.isChecked():
            suc = self.editHorizonMask(event=event, data=data)
        elif self.ui.checkEditBuildPoints.isChecked():
            suc = self.editBuildPoints(event=event, data=data, axes=axes)
        else:
            return False
        return suc

    def onMouseStar(self, event):
        """
        onMouseStar handles the mouse event in polar align mode. this means only a right
        click is possible and offers the opportunity to slew the telescope to the selected
        star and start manual polar alignment.

        :param event: mouse events
        :return: success
        """

        if not event.inaxes:
            return False
        if event.button == 1:
            alignType = 'polar'
        elif event.button == 3:
            alignType = 'ortho'
        else:
            return False
        if event.dblclick:
            return False

        hip = self.app.hipparcos
        plane = list(zip(hip.alt, hip.az))
        index = self.getIndexPoint(event=event, plane=plane, epsilon=2)
        if index is None:
            return False

        name = hip.name[index]
        ra, dec = hip.getAlignStarRaDecFromName(hip.name[index])

        textFormat = 'Align: {0}\nDo you want to slew the mount to:\n\n{1}'
        question = textFormat.format(alignType, name)
        msg = PyQt5.QtWidgets.QMessageBox
        reply = msg.question(self,
                             f'Hemisphere [{alignType.capitalize()}] align',
                             question,
                             msg.Yes | msg.No,
                             msg.No,
                             )
        if reply != msg.Yes:
            return False
        suc = self.app.mount.obsSite.setTargetRaDec(ra_hours=ra,
                                                    dec_degrees=dec,
                                                    )
        alt = self.app.mount.obsSite.Alt.degrees
        az = self.app.mount.obsSite.Az.degrees
        if suc:
            self.app.dome.slewDome(altitude=alt,
                                   azimuth=az,
                                   geometry=self.app.mainW.ui.checkDomeGeometry.isChecked()
                                   )
            suc = self.app.mount.obsSite.startSlewing(slewType=f'{alignType}')
        if not suc:
            self.app.message.emit(f'Cannot slew to: {name}', 2)
        else:
            self.app.message.emit('Starting slew', 0)
        return suc

    def onMouseDispatcher(self, event):
        """
        onMouseDispatcher dispatches the button events depending on the actual operation
        mode.

        :param event: button event for parsing
        :return:
        """

        if self.ui.checkEditNone.isChecked():
            self.onMouseNormal(event)
        elif self.ui.checkEditBuildPoints.isChecked():
            self.onMouseEdit(event)
        elif self.ui.checkEditHorizonMask.isChecked():
            self.onMouseEdit(event)
        elif self.ui.checkPolarAlignment.isChecked():
            self.onMouseStar(event)
