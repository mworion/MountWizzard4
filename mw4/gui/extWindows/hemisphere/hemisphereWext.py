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
            t = f'Slewing dome:        [{geoStat}],'
            t += f' AZ:[{azimuthT:3.1f}] delta: [{delta:3.1f}]'
            self.app.message.emit(t, 0)

        suc = self.app.mount.obsSite.startSlewing(slewType=slewType)

        if suc:
            t = f'Slewing mount to     AZ:[{azimuthT:3.1f}], ALT:[{altitudeT:3.1f}]'
            self.app.message.emit(t, 0)
        else:
            t = f'Cannot slew to       AZ:[{azimuthT:3.1f}], ALT:[{altitudeT:3.1f}]'
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

        question = '<b>Manual slewing to coordinate</b>'
        question += '<br><br>Selected coordinates are:<br>'
        question += f'<font color={self.M_BLUE}> Altitude: {altitude:3.1f}°'
        question += f'   Azimuth: {azimuth:3.1f}°</font>'
        question += '<br><br>Would you like to start slewing?<br>'

        suc = self.messageDialog(self, 'Slewing mount', question)
        if not suc:
            return False

        suc = self.app.mount.obsSite.setTargetAltAz(alt_degrees=altitude,
                                                    az_degrees=azimuth)
        if not suc:
            t = f'Cannot slew to       AZ:[{azimuth:3.1f}], ALT:[{altitude:3.1f}]'
            self.app.message.emit(t, 2)
            return False

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
        if not self.app.mount.model.numberStars:
            self.app.message.emit('No model for alignment present!', 2)
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
        question = '<b>Polar / Ortho Alignment procedure</b>'
        question += '<br><br>Selected alignment type: '
        question += f'<font color={self.M_BLUE}>{alignType}.</font>'
        question += '<br>Selected alignment star: '
        question += f'<font color={self.M_BLUE}>{name}.</font>'
        question += '<br>Would you like to start alignment?<br>'

        isDAT = self.app.mount.setting.statusDualAxisTracking
        warning = f'<br><i><font color={self.M_YELLOW}>'
        warning += 'Dual Axis Tracking is actually enabled!<br>'
        warning += 'It should be off during alignment process.</font></i>'

        question = question + warning if isDAT else question

        suc = self.messageDialog(self, 'Slewing mount', question)
        if not suc:
            return False

        suc = self.app.mount.obsSite.setTargetRaDec(ra_hours=ra,
                                                    dec_degrees=dec)
        if not suc:
            self.app.message.emit(f'Cannot slew to:      [{name}]', 2)
            return False

        self.app.message.emit(f'Align [{alignType}] to:    [{name}]', 1)
        suc = self.slewSelectedTarget(slewType=alignType)
        return suc
