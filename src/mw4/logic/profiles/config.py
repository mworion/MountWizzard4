# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from dataclasses import dataclass, field, fields
from typing import Any, Self

log: logging.Logger = logging.getLogger("MW4")
profileVersion = "5.0"
missing: Any = object()


def coerceValue(name: str, value: Any, default: Any) -> Any:
    """Return value if it fits the type of the default, otherwise the default.

    Numbers are interchangeable as the spin boxes store int or float.
    """
    if isinstance(default, bool):
        valid = isinstance(value, bool)
    elif isinstance(default, int | float):
        valid = isinstance(value, int | float) and not isinstance(value, bool)
    else:
        valid = isinstance(value, type(default))
    if valid:
        return value
    log.warning("Config key [%s] has invalid value [%r], using default", name, value)
    return default


@dataclass
class SectionBase:
    """Typed config section; keys of the persisted dict are the field names.

    Dict style access is kept for call sites not yet migrated to attributes.
    Keys unknown to the schema are kept in `extra` and written back unchanged.
    """

    extra: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def keys(cls) -> list[str]:
        return [f.name for f in fields(cls) if f.name != "extra"]

    @classmethod
    def fromDict(cls, data: dict[str, Any] | None) -> Self:
        section = cls()
        if not isinstance(data, dict):
            return section
        for key, value in data.items():
            section[key] = value
        return section

    def toDict(self) -> dict[str, Any]:
        result = {key: getattr(self, key) for key in self.keys()}
        result.update(self.extra)
        return result

    def __getitem__(self, key: str) -> Any:
        if key in self.keys():
            return getattr(self, key)
        return self.extra[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self.keys():
            default = getattr(type(self)(), key)
            setattr(self, key, coerceValue(key, value, default))
        else:
            self.extra[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self.keys() or key in self.extra

    def get(self, key: str, default: Any = None) -> Any:
        if key in self.keys():
            return getattr(self, key)
        return self.extra.get(key, default)

    def setdefault(self, key: str, default: Any = None) -> Any:
        if key not in self:
            self[key] = default
        return self[key]

    def pop(self, key: str, default: Any = missing) -> Any:
        if key in self.keys():
            value = getattr(self, key)
            setattr(self, key, getattr(type(self)(), key))
            return value
        if default is missing:
            return self.extra.pop(key)
        return self.extra.pop(key, default)


@dataclass
class MountParkConfig(SectionBase):
    ParkMountAfterSlew: bool = False


@dataclass
class SettingUpdateConfig(SectionBase):
    loglevelInfo: bool = False
    loglevelDebug: bool = True
    loglevelTrace: bool = False
    isOnline: bool = False
    ageDatabases: float = 1.0


@dataclass
class SettingGuiConfig(SectionBase):
    colorSet: int = 0
    transparency: float = 1.0
    scale: float = 1.0
    dpi: float = 96.0


@dataclass
class SettingAudioConfig(SectionBase):
    PlaySound: bool = False
    Volume: int = 1


@dataclass
class SettingDomeConfig(SectionBase):
    automaticDome: bool = False
    clearOpening: float = 0.4
    clearanceZenith: float = 0.2
    domeClearOpening: float = 0.4
    domeRadius: float = 1.5
    eastOffset: int = 0
    northOffset: int = 0
    offGEM: int = 0
    offLAT: int = 0
    openingHysteresis: float = 0.0
    radius: float = 1.5
    settleTime: int = 0
    use10micronDef: bool = False
    useDynamicFollowing: bool = False
    useGeometry: bool = False
    useOvershoot: bool = False
    verticalOffset: int = 0


@dataclass
class SettingRackConfig(SectionBase):
    rackCompMAC: str = "00:00:00:00:00"
    rackCompWolAddress: str = "255.255.255.255"
    rackCompWolPort: str = "9"


@dataclass
class WindowAnalyseConfig(SectionBase):
    linkViews: bool = False
    showHorizon: bool = False


@dataclass
class WindowHemisphereConfig(SectionBase):
    altitudeShift: int = 0
    azimuthShift: int = 0
    horizonMaskFileName: str = ""
    showAlignStar: bool = False
    showCelestial: bool = False
    showHorizon: bool = True
    showIsoModel: bool = False
    showMountLimits: bool = False
    showPolar: bool = False
    showSlewPath: bool = False
    showTerrain: bool = False
    tabWidget: int = 0
    terrainAlpha: float = 0.35
    terrainFileName: str = ""


@dataclass
class WindowImageConfig(SectionBase):
    aspectLocked: bool = False
    autoSolve: bool = False
    color: int = 0
    continous: bool = False
    embedData: bool = False
    flipH: bool = False
    flipV: bool = False
    imageFileName: str = ""
    isoLayer: bool = False
    offsetTiltAngle: int = 0
    photometryGroup: bool = False
    showCrosshair: bool = False
    showValues: bool = False
    snTarget: int = 0
    tabImage: int = 0
    timeTagImage: bool = True


@dataclass
class WindowMainConfig(SectionBase):
    altitudeMax: int = 75
    altitudeMin: int = 30
    aperture: int = 100
    asteroidSource: int = 0
    autoDeleteHorizon: bool = True
    autoDeleteMeridian: bool = False
    automaticTelescope: bool = False
    avoidFlip: bool = False
    avoidHorizon: bool = False
    binning1: int = 1
    binningN: int = 1
    buildPFileName: str = ""
    cometSource: int = 0
    conservativeTiming: bool = True
    coordsJ2000: bool = False
    coordsJNow: bool = False
    ditherBuildPoints: bool = False
    domeAutoFollowSat: bool = False
    exposureTime1: int = 1
    exposureTimeN: int = 1
    flexureAlt: int = 45
    flexureAz: int = 45
    flexureDuration: int = 60
    flexureTime: int = 30
    focalLength: int = 100
    focuserSteps: int = 100
    focuserStepsize: int = 100
    hysteresisMinAlt: int = 45
    hysteresisRuns: int = 1
    iersSource: int = 0
    includeSubdirs: bool = False
    keepGeneratedPoints: bool = False
    meridianDistanceFlip: int = 5
    moveDuration: int = 0
    moveStepSizeAltAz: int = 0
    mpcTab: int = 0
    newObjectName: str = ""
    noSort: bool = True
    normalTiming: bool = False
    numberBuildRetries: int = 0
    numberCelestialStepDEC: int = 15
    numberCelestialStepHA: int = 15
    numberDSOPoints: int = 15
    numberGridPointsCol: int = 6
    numberGridPointsRow: int = 5
    numberSpiral: int = 30
    optimizeOverall: bool = True
    optimizeSingle: bool = True
    parkMountAfterModel: bool = False
    progressiveTiming: bool = False
    refracCont: bool = False
    refracManual: bool = False
    refracNoTrack: bool = False
    refractionSource: str = ""
    retriesReverse: bool = False
    safetyMarginValue: int = 0
    satAfterFlip: bool = True
    satAltitudeMin: int = 30
    satBeforeFlip: bool = True
    satIsSunlit: bool = False
    satSource: int = 0
    satTwilight: int = 4
    slewSpeedHigh: bool = False
    slewSpeedLow: bool = True
    slewSpeedMax: bool = False
    slewSpeedMed: bool = False
    sortALT: bool = False
    sortAZ: bool = False
    sortDomeAZ: bool = False
    subFrame: int = 100
    targetRMS: int = 10
    trackingReplay: bool = False
    useInternalSatCalc: bool = False
    useSafetyMargin: bool = False
    waitTimeExposure: int = 0
    waitTimeFlip: int = 0


@dataclass
class WindowSimulatorConfig(SectionBase):
    domeTransparent: bool = False
    showBuildPoints: bool = False
    showHorizon: bool = False
    showLaser: bool = False
    showNumbers: bool = False
    showPointer: bool = False
    showSlewPath: bool = False


@dataclass
class ProfileConfig(SectionBase):
    """Root of the persisted profile. Sections without a schema live in `extra`."""

    profileName: str = "config"
    version: str = profileVersion
    topoLat: float = 51.47
    topoLon: float = 0.0
    topoElev: float = 46.0
    unitTimeUTC: bool = True
    MountPark: MountParkConfig = field(default_factory=MountParkConfig)
    SettingUpdate: SettingUpdateConfig = field(default_factory=SettingUpdateConfig)
    SettingGui: SettingGuiConfig = field(default_factory=SettingGuiConfig)
    SettingAudio: SettingAudioConfig = field(default_factory=SettingAudioConfig)
    SettingDome: SettingDomeConfig = field(default_factory=SettingDomeConfig)
    SettingRack: SettingRackConfig = field(default_factory=SettingRackConfig)
    WindowAnalyse: WindowAnalyseConfig = field(default_factory=WindowAnalyseConfig)
    WindowHemisphere: WindowHemisphereConfig = field(default_factory=WindowHemisphereConfig)
    WindowImage: WindowImageConfig = field(default_factory=WindowImageConfig)
    WindowMain: WindowMainConfig = field(default_factory=WindowMainConfig)
    WindowSimulator: WindowSimulatorConfig = field(default_factory=WindowSimulatorConfig)

    def __setitem__(self, key: str, value: Any) -> None:
        current = getattr(self, key, None)
        if isinstance(current, SectionBase) and isinstance(value, dict):
            setattr(self, key, type(current).fromDict(value))
        elif isinstance(current, SectionBase):
            setattr(self, key, value)
        else:
            super().__setitem__(key, value)

    def toDict(self) -> dict[str, Any]:
        result = super().toDict()
        for key in self.keys():
            value = result[key]
            if isinstance(value, SectionBase):
                result[key] = value.toDict()
        return result
