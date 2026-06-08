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
from PySide6.QtCore import QObject, QTimer, Signal


class PlateSolve:
    def __init__(self):
        from mw4.base.signalsDevices import Signals

        self.signals = Signals()
        self.framework = None
        self.run = {}
        self.deviceName = ""
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}

    @staticmethod
    def solve(a, b):
        return

    @staticmethod
    def abort():
        return

    @staticmethod
    def checkAvailability():
        return True, True


class CameraSignals(QObject):
    saved = Signal()
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)
    exposed = Signal()
    downloaded = Signal()


class Camera:
    def __init__(self):
        self.signals = CameraSignals()
        self.exposureTime = 0
        self.exposureTime1 = 0
        self.exposureTimeN = 0
        self.binning = 1
        self.binning1 = 1
        self.binningN = 1
        self.focalLength = 100
        self.subFrame = 100
        self.fastReadout = False
        self.data = {}
        self.framework = "indi"
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def expose(
        imagePath=None,
        exposureTime=None,
        binning=None,
        subFrame=None,
        fastReadout=None,
        focalLength=None,
        ra=None,
        dec=None,
    ):
        return

    @staticmethod
    def abort():
        return

    @staticmethod
    def sendCoolerTemp(temperature=None):
        return

    @staticmethod
    def sendOffset(offset=None):
        return

    @staticmethod
    def sendGain(gain=None):
        return

    @staticmethod
    def sendDownloadMode(fastReadout=None):
        return

    @staticmethod
    def sendCoolerSwitch(coolerOn=None):
        return

    @staticmethod
    def stopCommunication():
        return

    @staticmethod
    def startCommunication(loadConfig=None):
        return


class CoverSignals(QObject):
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Cover:
    def __init__(self):
        self.signals = CoverSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def closeCover():
        return

    @staticmethod
    def openCover():
        return

    @staticmethod
    def haltCover():
        return


class LightPanelSignals(QObject):
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class LightPanel:
    def __init__(self):
        self.signals = LightPanelSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def lightOn():
        return

    @staticmethod
    def lightOff():
        return

    @staticmethod
    def lightIntensity():
        return


class DomeSignals(QObject):
    message = Signal(object)
    azimuth = Signal()
    slewed = Signal()
    deviceDisconnected = Signal()
    deviceConnected = Signal()


class Dome:
    def __init__(self):
        self.domeShutterWidth = 0.6
        self.offGEM = 0
        self.offLAT = 0
        self.offNorth = 0
        self.offEast = 0
        self.domeRadius = 1.0
        self.clearOpening = 1
        self.data = {}
        self.framework = None
        self.signals = DomeSignals()
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def abortSlew():
        return

    @staticmethod
    def openShutter():
        return

    @staticmethod
    def closeShutter():
        return

    @staticmethod
    def slewDome(azimuth=0, altitude=0, follow=False):
        return

    @staticmethod
    def followDome(azimuth=0, altitude=0):
        return

    @staticmethod
    def avoidFirstOvershoot():
        return

    @staticmethod
    def slewCW():
        return

    @staticmethod
    def slewCCW():
        return


class SensorWeatherSignals(QObject):
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class SensorWeather:
    def __init__(self):
        self.signals = SensorWeatherSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}


class OnlineWeatherSignals(QObject):
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class OnlineWeather:
    def __init__(self):
        self.signals = OnlineWeatherSignals()
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.data = {}


class DirectWeatherSignals(QObject):
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class DirectWeather:
    def __init__(self):
        self.signals = DirectWeatherSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}


class SeeingWeatherSignals(QObject):
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)
    update = Signal()


class SeeingWeather:
    def __init__(self):
        self.signals = SeeingWeatherSignals()
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}
        self.data = {}


class FilterSignals(QObject):
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Filter:
    def __init__(self):
        self.signals = FilterSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def sendFilterNumber(filterNumber=None):
        return

    @staticmethod
    def sendFilterName(filterName=None):
        return


class FocuserSignals(QObject):
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Focuser:
    def __init__(self):
        self.signals = FocuserSignals()
        self.framework = None
        self.data = {}
        self.defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}
        self.run = {"indi": "dummy"}

    @staticmethod
    def move():
        return

    @staticmethod
    def halt():
        return


class MeasureSignals(QObject):
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class CSV:
    csvFilename = ""


class Measure:
    def __init__(self):
        self.signals = MeasureSignals()
        self.data = {}
        self.framework = None
        self.devices = {}
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.run = {"csv": CSV()}


class RelaySignals(QObject):
    message = Signal(object)
    statusReady = Signal()
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Relay:
    def __init__(self):
        self.signals = RelaySignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {}}
        self.timerTask = QTimer()

    @staticmethod
    def getRelay():
        return

    @staticmethod
    def pulse(a):
        return

    @staticmethod
    def switch(a):
        return


class RemoteSignals(QObject):
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Remote:
    def __init__(self):
        self.signals = RemoteSignals()
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {}}


class Telescope:
    class TelescopeSignals(QObject):
        message = Signal(object)
        deviceConnected = Signal(object)
        deviceDisconnected = Signal(object)

    class Test:
        deviceName = ""

    signals = TelescopeSignals()
    data = {}
    framework = None
    run = {"indi": Test()}
    focalLength = 100
    aperture = 100
    defaultConfig = {"framework": "", "frameworks": {"indi": {"dummy": {}}}}

    @staticmethod
    def stopCommunication():
        return

    @staticmethod
    def startCommunication(loadConfig=None):
        return


class Hipparcos:
    name = ["test"]
    az = [10]
    alt = [10]

    @staticmethod
    def calculateAlignStarPositionsAltAz():
        return

    @staticmethod
    def getAlignStarRaDecFromName():
        return


class PowerSignals(QObject):
    version = Signal()
    message = Signal(object)
    deviceConnected = Signal(object)
    deviceDisconnected = Signal(object)


class Power:
    def __init__(self):
        self.signals = PowerSignals()
        self.data = {}
        self.framework = None
        self.defaultConfig = {"framework": "", "frameworks": {}}

    @staticmethod
    def sendDew(port=None, value=None):
        return True

    @staticmethod
    def togglePowerPort(port=None):
        return True

    @staticmethod
    def togglePowerPortBoot(port=None):
        return True

    @staticmethod
    def toggleHubUSB():
        return True

    @staticmethod
    def togglePortUSB(port=None):
        return True

    @staticmethod
    def toggleAutoDew():
        return True

    @staticmethod
    def reboot():
        return True

    @staticmethod
    def sendAdjustableOutput(value=None):
        return True


class Data:
    SOLVED = 0
    UNPROCESSED = 1
    FAILED = 2

    def __init__(self):
        self.buildP = []
        self.horizonP = []

    @staticmethod
    def loadHorizonP(fileName=""):
        return

    @staticmethod
    def saveHorizonP(fileName=""):
        return

    @staticmethod
    def clear():
        return

    @staticmethod
    def clearBuildP():
        return

    @staticmethod
    def deleteCloseMeridian():
        return

    @staticmethod
    def addBuildP():
        return

    @staticmethod
    def saveBuildP():
        return

    @staticmethod
    def loadBuildP(a):
        return

    @staticmethod
    def genGrid(minAlt=None, maxAlt=None, numbRows=None, numbCols=None, keep=None):
        return

    @staticmethod
    def genAlign(altBase=None, azBase=None, numberBase=None, keep=None):
        return

    @staticmethod
    def genGreaterCircle(stepHA, StepDEC, distFlip):
        return

    @staticmethod
    def generateDSOPath(
        ha=None, dec=None, timeJD=None, location=None, numberPoints=None, keep=None
    ):
        return

    @staticmethod
    def generateGoldenSpiral(numberPoints=None, keep=None):
        return

    @staticmethod
    def generateCelestialEquator():
        return

    @staticmethod
    def deleteBelowHorizon():
        return

    @staticmethod
    def deleteCloseHorizonLine(a):
        return

    @staticmethod
    def ditherPoints():
        return

    @staticmethod
    def sortActualPierside():
        return

    @staticmethod
    def sortDomeAz():
        return

    @staticmethod
    def sortAz():
        return

    @staticmethod
    def sortAlt():
        return

    @staticmethod
    def setStatusBuildP(a, b):
        return

    @staticmethod
    def setStatusBuildPSolved(a):
        return

    @staticmethod
    def setStatusBuildPFailed(a):
        return

    @staticmethod
    def setStatusBuildPUnprocessed(a):
        return

    @staticmethod
    def isAboveHorizon(point):
        return True
