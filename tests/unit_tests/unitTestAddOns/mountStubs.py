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
# License APL2.0
#
###########################################################
import numpy as np
from dataclasses import dataclass, field
from packaging.version import Version
from PySide6.QtCore import QObject, Signal
from skyfield.api import Angle, Loader, load, wgs84


@dataclass
class DeviceConfigMount:
    deviceName: str = field(default="10micron")
    hostAddress: str = field(default="127.0.0.1")
    port: int = field(default=3492)
    MAC: str = field(default="00:00:00:00:00:00")
    clockSync: bool = field(default=False)
    syncTimeNone: bool = field(default=True)
    syncTimeCont: bool = field(default=False)
    syncTimeNotTrack: bool = field(default=False)
    wolAutomatic: bool = field(default=False)
    wolAddress: str = field(default="255.255.255.255")
    wolPort: int = field(default=9)


class Name:
    def __init__(self):
        self.name = ""
        self.jdStart = 1
        self.jdEnd = 1
        self.flip = False
        self.message = ""
        self.altitude = None
        self.azimuth = None


class MountSatellite:
    def __init__(self):
        self.tleParams = Name()
        self.trajectoryParams = Name()
        self.settlingTime = 0

    @staticmethod
    def setTLE(line0="", line1="", line2=""):
        return

    @staticmethod
    def slewTLE(julD=0, duration=0):
        return

    @staticmethod
    def calcTLE():
        return

    @staticmethod
    def calcTrajectory():
        return

    @staticmethod
    def setTrackingOffsets(Time=None, RA=None, DEC=None, DECcorr=None):
        return

    @staticmethod
    def clearTrackingOffsets():
        return


class MountModel:
    def __init__(self):
        self.starList = []
        self.nameList = []
        self.numberStars = 1
        self.errorRMS = 1
        self.terms = 1
        self.positionAngle = Angle(degrees=0)
        self.polarError = Angle(degrees=0)
        self.orthoError = Angle(degrees=0)
        self.azimuthError = Angle(degrees=0)
        self.altitudeError = Angle(degrees=0)
        self.altitudeTurns = 0
        self.azimuthTurns = 0

    @staticmethod
    def programModelFromStarList():
        return

    @staticmethod
    def clearModel():
        return

    @staticmethod
    def deleteName():
        return

    @staticmethod
    def storeName(a):
        return

    @staticmethod
    def loadName(a):
        return

    @staticmethod
    def parseStars(a, b):
        return

    @staticmethod
    def addStar(a):
        return

    @staticmethod
    def deletePoint(a):
        return


class MountFirmware:
    def __init__(self):
        self.product = "test"
        self.hardware = "test"
        self.vString = Version("0.0.0")
        self.date = "test"
        self.time = "test"

    @staticmethod
    def checkNewer(a):
        return True

    @staticmethod
    def isHW2024():
        return True

    @staticmethod
    def isHW2012():
        return True


class MountGeometry:
    def __init__(self):
        self.offNorth = 0
        self.offEast = 0
        self.offVert = 0
        self.offNorthGEM = 0
        self.offEastGEM = 0
        self.offVertGEM = 0
        self.offPlateOTA = 0
        self.offGemPlate = 0
        self.domeRadius = 100


class MountSetting:
    def __init__(self):
        self.meridianLimitSlew = 3
        self.meridianLimitTrack = 4
        self.horizonLimitHigh = 90
        self.horizonLimitLow = 0
        self.timeToFlip = 0
        self.statusUnattendedFlip = False
        self.statusDualAxisTracking = False
        self.statusRefraction = False
        self.refractionTemp = 0
        self.refractionPress = 0
        self.wakeOnLan = "None"
        self.autoPowerOn = "None"
        self.typeConnection = 1
        self.trackingRate = 60.2
        self.slewRateMin = 0
        self.slewRateMax = 1
        self.webInterfaceStat = True
        self.UTCExpire = None
        self.gpsSynced = True
        self.weatherTemperature = 0.0
        self.weatherPressure = 1000.0
        self.weatherDewPoint = 0.0
        self.weatherHumidity = 50
        self.weatherAge = 1
        self.settleTime = 0

    @staticmethod
    def timeToMeridian():
        return 0

    @staticmethod
    def setMeridianLimitSlew():
        return True

    @staticmethod
    def setMeridianLimitTrack():
        return True

    @staticmethod
    def setHorizonLimitLow():
        return True

    @staticmethod
    def setHorizonLimitHigh():
        return True

    @staticmethod
    def setSlewRate():
        return True

    @staticmethod
    def setUnattendedFlip():
        return True

    @staticmethod
    def setDualAxisTracking():
        return True

    @staticmethod
    def setRefractionTemp(a):
        return True

    @staticmethod
    def setRefractionPress(a):
        return True

    @staticmethod
    def setRefraction():
        return True

    @staticmethod
    def setWOL():
        return True

    @staticmethod
    def setAutoPower():
        return True

    @staticmethod
    def setSlewSpeedMax():
        return True

    @staticmethod
    def setSlewSpeedHigh():
        return True

    @staticmethod
    def setSlewSpeedMed():
        return True

    @staticmethod
    def setSlewSpeedLow():
        return True

    @staticmethod
    def checkRateSidereal():
        return False

    @staticmethod
    def checkRateLunar():
        return False

    @staticmethod
    def checkRateSolar():
        return False

    @staticmethod
    def setLunarTracking():
        return True

    @staticmethod
    def setSolarTracking():
        return True

    @staticmethod
    def setSiderealTracking():
        return True

    @staticmethod
    def setWebInterface():
        return True

    @staticmethod
    def setDirectWeatherUpdateType(a):
        return True

    @staticmethod
    def setSettleTime(a):
        return True

    @staticmethod
    def setRefractionParam(temperature=20, pressure=900):
        return True


class MountSignals(QObject):
    locationDone = Signal(object)
    settingDone = Signal(object)
    pointDone = Signal(object)
    mountIsUp = Signal(object)
    firmwareDone = Signal(object)
    calcTLEdone = Signal(object)
    getTLEdone = Signal(object)
    getModelDone = Signal(object)
    alert = Signal()
    namesDone = Signal(object)
    slewed = Signal()
    calcTrajectoryDone = Signal(object)
    calcProgress = Signal(object)
    deviceConnected = Signal(str)
    deviceDisconnected = Signal(str)


class MountObsSite:
    def __init__(self):
        self.Alt = Angle(degrees=0)
        self.Az = Angle(degrees=0)
        self.haJNowTarget = Angle(hours=0)
        self.decJNowTarget = Angle(degrees=0)
        self.angularPosRA = Angle(degrees=0)
        self.angularPosDEC = Angle(degrees=0)
        self.errorAngularPosRA = Angle(degrees=0)
        self.errorAngularPosDEC = Angle(degrees=0)
        self.raJNow = Angle(hours=0)
        self.decJNow = Angle(degrees=0)
        self.haJNow = Angle(hours=0)
        self.AzTarget = Angle(degrees=0)
        self.AltTarget = Angle(degrees=0)
        self.pierside = "E"
        self.piersideTarget = "E"
        self.timeSidereal = Angle(hours=12)
        self.location = wgs84.latlon(
            latitude_degrees=20, longitude_degrees=10, elevation_m=500
        )
        self.ts = load.timescale(builtin=True)
        self.timeJD = self.ts.tt_jd(2459580.5)
        self.timeDiff = 0
        self.loader = Loader("tests/work/data", verbose=False)
        self.status = 0
        self.statusSat = "E"
        self.UTC2TT = 69.184

    @property
    def isTracking(self) -> bool:
        return self.status == 0

    @property
    def isStopped(self) -> bool:
        return self.status == 1

    @property
    def isParked(self) -> bool:
        return self.status == 5

    @property
    def isFollowingSatellite(self) -> bool:
        return self.status == 10

    @staticmethod
    def setLongitude(a):
        return True

    @staticmethod
    def setLatitude(a):
        return True

    @staticmethod
    def setElevation(a):
        return True

    @staticmethod
    def startTracking():
        return True

    @staticmethod
    def stopTracking():
        return True

    @staticmethod
    def park():
        return True

    @staticmethod
    def unpark():
        return True

    @staticmethod
    def flip():
        return True

    @staticmethod
    def stop():
        return True

    @staticmethod
    def stopMoveAll():
        return True

    @staticmethod
    def moveNorth():
        return True

    @staticmethod
    def stopMoveNorth():
        return True

    @staticmethod
    def moveEast():
        return True

    @staticmethod
    def stopMoveEast():
        return True

    @staticmethod
    def moveWest():
        return True

    @staticmethod
    def stopMoveWest():
        return True

    @staticmethod
    def moveSouth():
        return True

    @staticmethod
    def stopMoveSouth():
        return True

    @staticmethod
    def startSlewing(slewType=None):
        return True

    @staticmethod
    def adjustClock(a):
        return True

    @staticmethod
    def setTargetAltAz(alt_degrees=0, az_degrees=0):
        return True

    @staticmethod
    def setTargetRaDec(ra_hours=0, dec_degrees=0):
        return True

    @staticmethod
    def setLocation(loc):
        return True

    @staticmethod
    def syncPositionToTarget():
        return True

    @staticmethod
    def parkOnActualPosition():
        return True


class Mount(QObject):
    def __init__(self):
        super().__init__()
        self.signals = MountSignals()
        self.obsSite = MountObsSite()
        self.geometry = MountGeometry()
        self.firmware = MountFirmware()
        self.setting = MountSetting()
        self.satellite = MountSatellite()
        self.model = MountModel()
        self.host = None
        self.MAC = None
        self.loggingTrace = False
        self.stat = False
        self.instance = self
        self.framework = "mountcontrol"
        self.config = DeviceConfigMount()

        class FrameworkConfig:
            config = DeviceConfigMount()

        self.run = {"mountcontrol": FrameworkConfig()}

    @staticmethod
    def getFW():
        return True

    @staticmethod
    def bootMount():
        return True

    @staticmethod
    def shutdown():
        return True

    @staticmethod
    def getLocation():
        return True

    @staticmethod
    def calcTLE():
        return

    @staticmethod
    def getTLE():
        return

    @staticmethod
    def progTrajectory():
        return

    @staticmethod
    def startMountClockTimer():
        return

    @staticmethod
    def stopMountClockTimer():
        return

    @staticmethod
    def calcTransformationMatricesTarget():
        return

    @staticmethod
    def calcMountAltAzToDomeAltAz():
        return

    @staticmethod
    def calcTransformationMatricesActual():
        return (1, 1, np.array([0, 0, 0]), np.array([0, 0, 0]), np.array([0, 0, 0]))

    @staticmethod
    def syncPositionToTarget():
        return

    @staticmethod
    def getModel():
        return

    @staticmethod
    def getNames():
        return
