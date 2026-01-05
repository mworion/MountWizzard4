############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################
import logging
from mw4.base.transform import J2000ToJNow
from skyfield.api import Angle


class SlewInterface:
    """ """

    log = logging.getLogger("MW4")

    def __init__(self, parent):
        """ """
        self.app = parent.app
        self.msg = parent.msg

    def slewSelectedTargetWithDome(self, slewType: str = "normal") -> bool:
        """ """
        azimuthT = self.app.mount.obsSite.AzTarget
        altitudeT = self.app.mount.obsSite.AltTarget

        if self.app.deviceStat["dome"]:
            delta = self.app.dome.slewDome(altitudeT.degrees, azimuthT.degrees)
            geoStat = "Geometry corrected" if delta else "Equal mount"
            text = f"{geoStat}"
            text += f", az: {azimuthT.degrees:3.1f} delta: {delta:3.1f}"
            self.app.msg.emit(0, "Tools", "Slewing dome", text)

        suc = self.app.mount.obsSite.startSlewing(slewType=slewType)
        if suc:
            self.msg.emit(0, "Tools", "Slewing mount", "Slew to target")
        else:
            self.msg.emit(2, "Tools", "Slewing error", "Cannot slew to target")
        return suc

    def slewTargetAltAz(self, alt: Angle, az: Angle, slewType: str = "normal") -> bool:
        """ """
        suc = self.app.mount.obsSite.setTargetAltAz(alt, az)
        if not suc:
            t = f"Cannot slew to Az:[{az.degrees:3.1f}], Alt:[{alt.degrees:3.1f}]"
            self.msg.emit(2, "Tools", "Slewing error", t)
            return False

        suc = self.slewSelectedTargetWithDome(slewType=slewType)
        return suc

    def slewTargetRaDec(
        self, ra: Angle, dec: Angle, slewType: str = "normal", epoch: str = "J2000"
    ) -> bool:
        """ """
        timeJD = self.app.mount.obsSite.timeJD
        if epoch == "J2000":
            raJNow, decJNow = J2000ToJNow(ra, dec, timeJD)
        else:
            raJNow = ra
            decJNow = dec

        suc = self.app.mount.obsSite.setTargetRaDec(raJNow, decJNow)
        if not suc:
            t = f"Cannot slew to RA:[{raJNow.hours:3.1f}], "
            t += f"DEC:[{decJNow.degrees:3.1f}]"
            self.msg.emit(2, "Tools", "Slewing error", t)
            return False

        return self.slewSelectedTargetWithDome(slewType=slewType)
