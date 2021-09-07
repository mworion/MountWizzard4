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
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtGui import QGuiApplication, QCursor
from PyQt5.QtCore import Qt
import numpy as np
import matplotlib.path as mpath

# local import


class HemisphereWindowExt:
    """
    the HemisphereWindowExt window class handles

    """

    __all__ = ['HemisphereWindowExt',
               ]

    @staticmethod
    def markerPoint():
        """
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
        :return: marker
        """
        circleB = mpath.Path.unit_circle()
        circleM = mpath.Path.unit_circle()
        circleS = mpath.Path.unit_circle()
        circleC = mpath.Path.unit_circle()
        verts = np.concatenate([circleB.vertices,
                                0.8 * circleM.vertices,
                                0.15 * circleS.vertices,
                                0.1 * circleC.vertices])
        codes = np.concatenate([circleB.codes,
                                circleM.codes,
                                circleS.codes,
                                circleC.codes])
        marker = mpath.Path(verts, codes)
        return marker

    @staticmethod
    def markerStar():
        """
        :return: marker
        """
        star = mpath.Path.unit_regular_star(8)
        verts = np.concatenate([star.vertices])
        codes = np.concatenate([star.codes])
        marker = mpath.Path(verts, codes)
        return marker

    def setOperationMode(self):
        """
        setOperationMode changes the operation mode of the hemisphere window(s)
        depending on the choice, colors and styles will be changed.

        :return: success
        """
        if self.ui.checkEditNone.isChecked():
            self.operationMode = 'normal'
            self.ui.addPositionToHorizon.setEnabled(False)

        elif self.ui.checkEditBuildPoints.isChecked():
            self.operationMode = 'build'
            self.ui.addPositionToHorizon.setEnabled(False)

        elif self.ui.checkEditHorizonMask.isChecked():
            self.operationMode = 'horizon'
            self.ui.addPositionToHorizon.setEnabled(True)

        elif self.ui.checkPolarAlignment.isChecked():
            self.ui.checkShowAlignStar.setChecked(True)
            self.operationMode = 'star'
            self.ui.addPositionToHorizon.setEnabled(False)

        self.drawHemisphere()
        return True

    def enableEditPoints(self, status):
        """
        :param status:
        :return:
        """
        self.ui.operationMode.setEnabled(status)
        hem = self.hemisphereMat.figure.canvas
        if status:
            self.hemMouse = hem.mpl_connect('button_press_event',
                                            self.onMouseDispatcher)
        else:
            hem.mpl_disconnect(self.hemMouse)
        return True

    def showMouseCoordinates(self, event):
        """
        :param event:
        :return: success
        """
        if not event.inaxes:
            xText = '-'
            yText = '-'
            QGuiApplication.setOverrideCursor(QCursor(Qt.ArrowCursor))
        else:
            xText = f'{event.xdata:3.1f}'
            yText = f'{event.ydata:3.1f}'
            QGuiApplication.setOverrideCursor(QCursor(Qt.CrossCursor))

        self.ui.altitude.setText(yText)
        self.ui.azimuth.setText(xText)
        return True

    def slewSelectedTarget(self, slewType='normal'):
        """
        :param slewType:
        :return: success
        """
        azimuthT = self.app.mount.obsSite.AzTarget.degrees
        altitudeT = self.app.mount.obsSite.AltTarget.degrees

        if self.app.deviceStat['dome']:
            self.app.dome.avoidFirstOvershoot()
            delta = self.app.dome.slewDome(altitude=altitudeT,
                                           azimuth=azimuthT)

            geoStat = 'Geometry corrected' if delta else 'Equal mount'
            t = f'Slewing dome:        {geoStat},'
            t += f' az: {azimuthT:3.1f} delta: {delta:3.1f}'
            self.app.message.emit(t, 0)

        suc = self.app.mount.obsSite.startSlewing(slewType=slewType)

        if suc:
            t = f'Slewing mount to AZ: [{azimuthT}], ALT: [{altitudeT}]'
            self.app.message.emit(t, 0)
        else:
            t = f'Cannot slew to AZ: [{azimuthT}], ALT: [{altitudeT}]'
            self.app.message.emit(t, 2)

        return suc

    def onMouseNormal(self, event):
        """
        onMouseNormal handles the mouse event in normal mode. this means only
        a double click is possible and offers the opportunity to slew the
        telescope to a certain position in sky selected by the mouse.

        :param event: mouse events
        :return: success
        """
        if not event.inaxes:
            return False
        if event.button != 1 or not event.dblclick:
            return False

        azimuth = int(event.xdata + 0.5)
        altitude = int(event.ydata + 0.5)

        question = 'Do you want to slew the mount to:'
        question += f'\n\nAzimuth:\t{azimuth}°\nAltitude:\t{altitude}°'
        suc = self.messageDialog(self, 'Slewing mount', question)
        if not suc:
            return False

        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=altitude,
                                                    az_degrees=azimuth)
        if not suc:
            t = f'Cannot slew to AZ: [{azimuth}], ALT: [{altitude}]'
            self.app.message.emit(t, 2)
            return False

        t = f'Slewing mount to AZ: [{azimuth}], ALT: [{altitude}]'
        self.app.message.emit(t, 0)
        suc = self.slewSelectedTarget(slewType='keep')
        return suc

    def addHorizonPointManual(self):
        """
        :return:
        """
        data = self.app.data
        alt = self.app.mount.obsSite.Alt
        az = self.app.mount.obsSite.Az

        if alt is None or az is None:
            return False

        index = self.getIndexPointX(x=az.degrees, plane=data.horizonP)
        if index is None and data.horizonP:
            return False

        suc = data.addHorizonP(value=(alt.degrees, az.degrees), position=index)
        if suc:
            self.drawHemisphere()
        return suc

    def addHorizonPoint(self, data=None, event=None):
        """
        addHorizonPoint calculates from the position of the left mouse click the
        position where the next horizon point should be added. the coordinates
        are given from mouse click itself.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return:
        """
        index = self.getIndexPointX(x=event.xdata, plane=data.horizonP)
        if index is None and data.horizonP:
            return False

        suc = data.addHorizonP(value=(event.ydata, event.xdata),
                               position=index)
        return suc

    def deleteHorizonPoint(self, data=None, event=None):
        """
        deleteHorizonPoint selects the next horizon point in distance max and
        tries to delete it. there have to be at least 2 horizon point left.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return: success
        """
        index = self.getIndexPoint(event=event, plane=data.horizonP)

        if index is None:
            return False

        suc = False
        if len(data.horizonP) > 0:
            suc = data.delHorizonP(position=index)

        return suc

    def editHorizonMask(self, data=None, event=None):
        """
        editHorizonMask does dispatching the different mouse clicks for adding
        or deleting horizon mask points and call the function accordingly.

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

        if data.horizonP is None:
            return False

        self.drawHemisphere()
        return suc

    def addBuildPoint(self, data=None, event=None):
        """
        addBuildPoint calculates from the position of the left mouse click the
        position where the next modeldata point should be added. the coordinates
        are given from mouse click itself.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return:
        """
        self.app.buildPointsChanged.emit()
        index = self.getIndexPoint(event=event, plane=data.buildP, epsilon=360)
        if index is None:
            return False

        index += 1
        suc = data.addBuildP(value=(event.ydata, event.xdata, True),
                             position=index)
        if not suc:
            return False

        return True

    def deleteBuildPoint(self, data=None, event=None):
        """
        deleteBuildPoint selects the next modeldata point in distance max and
        tries to delete it. there have to be at least 2 horizon point left.

        :param data: point in tuples (alt, az)
        :param event: mouse event
        :return: success
        """
        self.app.buildPointsChanged.emit()
        index = self.getIndexPoint(event=event, plane=data.buildP)
        if index is None:
            return False

        suc = data.delBuildP(position=index)
        return suc

    def editBuildPoints(self, data=None, event=None):
        """
        editBuildPoints does dispatching the different mouse clicks for adding
        or deleting model data points and call the function accordingly.

        :param data: points in tuples (alt, az)
        :param event: mouse event
        :return: success
        """
        if event.button == 1:
            suc = self.addBuildPoint(data=data, event=event)
        elif event.button == 3:
            suc = self.deleteBuildPoint(data=data, event=event)
        else:
            return False

        self.drawHemisphere()
        return suc

    def onMouseEdit(self, event):
        """
        onMouseEdit handles the mouse event in normal mode. this means depending
        on the edit mode (horizon or model points) a left click adds a new point
        and right click deletes the selected point.

        :param event: mouse events
        :return: success
        """
        data = self.app.data
        if not event.inaxes:
            return False
        if event.dblclick:
            return False

        if self.ui.checkEditHorizonMask.isChecked():
            suc = self.editHorizonMask(event=event, data=data)
        elif self.ui.checkEditBuildPoints.isChecked():
            suc = self.editBuildPoints(event=event, data=data)
        else:
            return False

        return suc

    def onMouseStar(self, event):
        """
        onMouseStar handles the mouse event in polar align mode. this means
        only a right click is possible and offers the opportunity to slew the
        telescope to the selected star and start manual polar alignment.

        :param event: mouse events
        :return: success
        """
        if not event.inaxes:
            return False

        if event.button == 1 and not event.dblclick:
            alignType = 'polar'
        elif event.button == 3 and not event.dblclick:
            alignType = 'ortho'
        else:
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

        suc = self.messageDialog(self, 'Slewing mount', question)
        if not suc:
            return False

        suc = self.app.mount.obsSite.setTargetRaDec(ra_hours=ra,
                                                    dec_degrees=dec)
        if not suc:
            self.app.message.emit(f'Cannot slew to: [{name}]', 2)
            return False

        self.app.message.emit(f'Slewing mount to: [{name}]', 2)
        suc = self.slewSelectedTarget(slewType=alignType)
        return suc

    def onMouseDispatcher(self, event):
        """
        onMouseDispatcher dispatches the button events depending on the actual
        operation mode.

        :param event: button event for parsing
        :return: True for test purpose
        """
        if self.ui.checkEditNone.isChecked():
            self.onMouseNormal(event)

        elif self.ui.checkEditBuildPoints.isChecked():
            self.onMouseEdit(event)

        elif self.ui.checkEditHorizonMask.isChecked():
            self.onMouseEdit(event)

        elif self.ui.checkPolarAlignment.isChecked():
            self.onMouseStar(event)
        return True
