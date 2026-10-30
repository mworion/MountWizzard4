# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
# Module (c) 2026 from Rüdiger Proske
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from mw4.deviceRegistry import DeviceRegistry
from pathlib import Path
from typing import Any

SOURCE_PROFILE_VERSION = "4.1"
TARGET_PROFILE_VERSION = "5.0"

# Top-level settings retained by v5.
TOP_LEVEL_KEYS = (
    "showAnalyseW",
    "showHemisphereW",
    "showImageW",
    "showKeypadW",
    "showMeasureW",
    "showMessageW",
    "showSimulatorW",
    "showVideoW1",
    "showVideoW2",
    "showVideoW3",
    "showVideoW4",
    "topoElev",
    "topoLat",
    "topoLon",
)

# mainW -> WindowMain fields with unchanged meaning.
WINDOW_MAIN_SAME = (
    "altitudeMax",
    "altitudeMin",
    "aperture",
    "autoDeleteHorizon",
    "autoDeleteMeridian",
    "automaticTelescope",
    "avoidFlip",
    "avoidHorizon",
    "binningN",
    "buildPFileName",
    "conservativeTiming",
    "coordsJ2000",
    "coordsJNow",
    "ditherBuildPoints",
    "domeAutoFollowSat",
    "focalLength",
    "focuserSteps",
    "focuserStepsize",
    "iersSource",
    "includeSubdirs",
    "keepGeneratedPoints",
    "moveDuration",
    "moveStepSizeAltAz",
    "newObjectName",
    "normalTiming",
    "numberBuildRetries",
    "numberDSOPoints",
    "numberGridPointsCol",
    "numberGridPointsRow",
    "numberSpiral",
    "optimizeOverall",
    "optimizeSingle",
    "parkMountAfterModel",
    "progressiveTiming",
    "refracCont",
    "refracManual",
    "refracNoTrack",
    "refractionSource",
    "rename1",
    "rename2",
    "rename3",
    "rename4",
    "rename5",
    "rename6",
    "retriesReverse",
    "safetyMarginValue",
    "satAfterFlip",
    "satAltitudeMin",
    "satBeforeFlip",
    "satIsSunlit",
    "satTwilight",
    "slewSpeedHigh",
    "slewSpeedLow",
    "slewSpeedMax",
    "slewSpeedMed",
    "subFrame",
    "targetRMS",
    "useInternalSatCalc",
    "useSafetyMargin",
    "waitTimeExposure",
    "waitTimeFlip",
)

WINDOW_MAIN_RENAMED = (
    ("binning", "binning1"),
    ("expTime", "exposureTime1"),
    ("expTimeN", "exposureTimeN"),
    ("filterSatellite", "satFilterText"),
    ("satelliteSource", "satSource"),
)

MOUNT_MAPPING = (
    ("mainW.mountHost", "hostAddress", None),
    ("mainW.mountMAC", "MAC", None),
    ("mainW.mountWolAddress", "wolAddress", None),
    ("mainW.mountWolPort", "wolPort", int),
    ("mainW.automaticWOL", "wolAutomatic", bool),
    ("mainW.syncTimeCont", "syncTimeCont", bool),
    ("mainW.syncTimeNone", "syncTimeNone", bool),
    ("mainW.syncTimeNotTrack", "syncTimeNotTrack", bool),
    ("mainW.port3492", "port", lambda enabled: 3492 if enabled else 3490),
)

DOME_MAPPING = (
    ("automaticDome", "automaticDome"),
    ("domeClearOpening", "clearOpening"),
    ("domeClearanceZenith", "clearanceZenith"),
    ("domeEastOffset", "eastOffset"),
    ("domeNorthOffset", "northOffset"),
    ("domeOpeningHysteresis", "openingHysteresis"),
    ("domeRadius", "radius"),
    ("domeZoffGEM", "verticalOffset"),
    ("offGEM", "offGEM"),
    ("offLAT", "offLAT"),
    ("settleTimeDome", "settleTime"),
    ("useDynamicFollowing", "useDynamicFollowing"),
    ("useOvershoot", "useOvershoot"),
    ("useDomeGeometry", "useGeometry"),
)

UPDATE_MAPPING = (
    ("isOnline", "isOnline"),
    ("loglevelDebug", "loglevelDebug"),
    ("loglevelStandard", "loglevelInfo"),
    ("loglevelTrace", "loglevelTrace"),
)

AUDIO_MAPPING = {
    "soundConnectionLost": "ConnectionLost",
    "soundDomeSlewFinished": "DomeSlew",
    "soundImageSaved": "ImageSaved",
    "soundImageSolved": "ImageSolved",
    "soundMountAlert": "MountAlert",
    "soundMountSlewFinished": "MountSlew",
    "soundRunFinished": "RunFinished",
    "soundSatStartTracking": "SatStartTracking",
}

# Hemisphere/horizon state, including the referenced horizon and terrain names.
HEMISPHERE_KEYS = (
    "showSlewPath",
    "showMountLimits",
    "showCelestial",
    "showAlignStar",
    "showHorizon",
    "showPolar",
    "showTerrain",
    "showIsoModel",
    "tabWidget",
    "terrainAlpha",
    "azimuthShift",
    "altitudeShift",
    "horizonMaskFileName",
    "terrainFileName",
    "height",
    "width",
    "winPosX",
    "winPosY",
)

RENAMED_DEVICE_FIELDS = {
    "hostaddress": "hostAddress",
    "messages": "showMessage",
}

PLAIN_DEVICES = (
    "cover",
    "dome",
    "filter",
    "focuser",
    "power",
    "telescope",
    "plateSolve",
    "directWeather",
    "seeingWeather",
    "relay",
    "measure",
)


@dataclass
class MigrationData:
    config: dict[str, Any]
    mapped: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class ImportResult:
    source: Path
    target: Path | None
    status: str
    mapped: int = 0
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    error: str = ""


def _getPath(data: dict[str, Any], path: str, default: Any = None) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def _setPath(data: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    current = data
    for part in parts[:-1]:
        child = current.get(part)
        if not isinstance(child, dict):
            child = {}
            current[part] = child
        current = child
    current[parts[-1]] = value


def deviceSchemaFromRegistry(deviceRegistry: DeviceRegistry) -> dict[str, dict[str, set[str]]]:
    """Read valid framework/config field names from the running MW4 registry.

    Only names are used. No values from the current profile are copied into an
    imported profile.
    """
    schema: dict[str, dict[str, set[str]]] = {}
    for deviceName in deviceRegistry:
        entry = deviceRegistry[deviceName]
        frameworkSchema: dict[str, set[str]] = {}
        for frameworkName, driver in getattr(entry, "run", {}).items():
            config = getattr(driver, "config", None)
            if config is None or not is_dataclass(config):
                continue
            frameworkSchema[frameworkName] = {item.name for item in fields(config)}
        if frameworkSchema:
            schema[deviceName] = frameworkSchema
    return schema


class LegacyMigrator:
    """Convert one legacy schema-4.1 profile to a sparse schema-5.0 profile."""

    def __init__(
        self,
        old: dict[str, Any],
        deviceSchema: dict[str, dict[str, set[str]]],
    ) -> None:
        self.old = old
        self.deviceSchema = deviceSchema
        self.target: dict[str, Any] = {
            "profileName": str(old.get("profileName") or "config"),
            "version": TARGET_PROFILE_VERSION,
        }
        self.mapped: list[tuple[str, str]] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []
        self.missing = object()

    def mapValue(
        self,
        sourcePath: str,
        targetPath: str,
        transform: Any = None,
    ) -> None:
        value = _getPath(self.old, sourcePath, self.missing)
        if value is self.missing:
            return
        if transform is not None:
            try:
                value = transform(value)
            except (TypeError, ValueError) as exc:
                self.warnings.append(
                    f"{sourcePath}: value could not be converted for {targetPath}: {exc}"
                )
                return
        _setPath(self.target, targetPath, value)
        self.mapped.append((sourcePath, targetPath))

    def mapGeneral(self) -> None:
        for key in TOP_LEVEL_KEYS:
            if key in self.old:
                self.mapValue(key, key)
        self.mapValue("mainW.unitTimeUTC", "unitTimeUTC")
        self.mapValue("colorSet", "SettingGui.colorSet")

    def mapWindowMain(self) -> None:
        for key in WINDOW_MAIN_SAME:
            self.mapValue(f"mainW.{key}", f"WindowMain.{key}")
        for sourceKey, targetKey in WINDOW_MAIN_RENAMED:
            self.mapValue(f"mainW.{sourceKey}", f"WindowMain.{targetKey}")

        mainW = self.old.get("mainW", {})
        if "renameDir" in mainW:
            self.notes.append("mainW.renameDir not imported because it belongs to the old workdir")
        if "useDomeAz" in mainW:
            self.notes.append("mainW.useDomeAz not imported because no proven v5 equivalent exists")

    def mapMount(self) -> None:
        """Check field existence against the current runtime schema."""
        _setPath(self.target, "SettingDeviceMount.framework", "10micron")
        mountFields = self.deviceSchema.get("mount", {}).get("10micron", set())
        for sourcePath, targetKey, transform in MOUNT_MAPPING:
            if targetKey not in mountFields:
                self.warnings.append(f"Current MW4 mount schema has no field {targetKey!r}")
                continue
            self.mapValue(sourcePath, f"SettingDeviceMount.10micron.{targetKey}", transform)

    def mapDome(self) -> None:
        for sourceKey, targetKey in DOME_MAPPING:
            self.mapValue(f"mainW.{sourceKey}", f"SettingDome.{targetKey}")

    def mapPark(self) -> None:
        self.mapValue("mainW.parkMountAfterSlew", "MountPark.ParkMountAfterSlew")
        for index in range(10):
            self.mapValue(f"mainW.posAlt{index}", f"SettingPark.ParkAlt{index}")
            self.mapValue(f"mainW.posAz{index}", f"SettingPark.ParkAz{index}")
            self.mapValue(f"mainW.posText{index}", f"SettingPark.ParkText{index}")

    def mapRelay(self) -> None:
        for index in range(8):
            self.mapValue(f"mainW.relay{index}index", f"SettingRelay.Action{index}", int)
            text = _getPath(self.old, f"mainW.relay{index}buttonText", "")
            if text:
                self.mapValue(f"mainW.relay{index}buttonText", f"SettingRelay.RelayText{index}")

    def mapMisc(self) -> None:
        self.mapValue("mainW.rackCompMAC", "SettingRack.rackCompMAC")
        for sourceKey, targetKey in UPDATE_MAPPING:
            self.mapValue(f"mainW.{sourceKey}", f"SettingUpdate.{targetKey}")
        for sourceKey, targetKey in AUDIO_MAPPING.items():
            self.mapValue(f"mainW.{sourceKey}", f"SettingAudio.{targetKey}", int)
        for key in ("height", "winPosX", "winPosY"):
            self.mapValue(f"messageW.{key}", f"WindowMessage.{key}")
        for key in HEMISPHERE_KEYS:
            self.mapValue(f"hemisphereW.{key}", f"WindowHemisphere.{key}")

    def copyFrameworks(
        self,
        oldDevice: str,
        targetDevice: str,
        aliases: dict[str, str],
    ) -> None:
        sourceDevice = self.old.get("driversData", {}).get(oldDevice, {})
        targetFrameworks = self.deviceSchema.get(targetDevice, {})
        for oldFramework, sourceBlock in sourceDevice.get("frameworks", {}).items():
            newFramework = aliases.get(oldFramework, oldFramework)
            validFields = targetFrameworks.get(newFramework)
            if not validFields or not isinstance(sourceBlock, dict):
                continue
            self.copyFields(
                oldDevice, oldFramework, targetDevice, newFramework, sourceBlock, validFields
            )

    def copyFields(
        self,
        oldDevice: str,
        oldFramework: str,
        targetDevice: str,
        newFramework: str,
        sourceBlock: dict[str, Any],
        validFields: set[str],
    ) -> None:
        for sourceKey, sourceValue in sourceBlock.items():
            targetKey = RENAMED_DEVICE_FIELDS.get(sourceKey, sourceKey)
            if sourceKey == "deviceList" or targetKey not in validFields:
                continue
            if (
                targetKey == "hostAddress"
                and isinstance(sourceValue, str)
                and sourceValue.lower() == "localhost"
            ):
                sourceValue = "127.0.0.1"
            targetPath = f"SettingDevice.{targetDevice}.{newFramework}.{targetKey}"
            _setPath(self.target, targetPath, sourceValue)
            sourcePath = f"driversData.{oldDevice}.frameworks.{oldFramework}.{sourceKey}"
            self.mapped.append((sourcePath, targetPath))

    def copyActiveFramework(
        self,
        oldDevice: str,
        targetDevice: str,
        aliases: dict[str, str],
    ) -> None:
        sourceDevice = self.old.get("driversData", {}).get(oldDevice, {})
        activeFramework = sourceDevice.get("framework", "")
        if not activeFramework:
            return
        targetFramework = aliases.get(activeFramework, activeFramework)
        if targetFramework in self.deviceSchema.get(targetDevice, {}):
            targetPath = f"SettingDevice.{targetDevice}.framework"
            _setPath(self.target, targetPath, targetFramework)
            self.mapped.append((f"driversData.{oldDevice}.framework", targetPath))
        else:
            self.warnings.append(
                f"{oldDevice}: active framework {activeFramework!r} has no direct "
                "v5 target and was left disabled"
            )

    def copyDevice(
        self,
        oldDevice: str,
        newDevice: str | None = None,
        aliases: dict[str, str] | None = None,
    ) -> None:
        targetDevice = newDevice or oldDevice
        frameworkAliases = aliases or {}
        self.copyFrameworks(oldDevice, targetDevice, frameworkAliases)
        self.copyActiveFramework(oldDevice, targetDevice, frameworkAliases)

    def mapDevices(self) -> None:
        """Valid v5 field names come from the running DeviceRegistry."""
        for deviceName in PLAIN_DEVICES:
            self.copyDevice(deviceName)
        self.copyDevice("remote", aliases={"internal": "tcp"})
        self.copyDevice("camera")
        self.copyDevice("sensorWeather", "sensor1Weather")
        self.copyDevice("powerWeather", "sensor2Weather")
        self.copyDevice("skymeter", "sensor3Weather")
        self.copyDevice("onlineWeather", "sensor4Weather", {"onlineWeather": "online"})

    def run(self) -> MigrationData:
        self.mapGeneral()
        self.mapWindowMain()
        self.mapMount()
        self.mapDome()
        self.mapPark()
        self.mapRelay()
        self.mapMisc()
        self.mapDevices()
        return MigrationData(
            config=self.target,
            mapped=self.mapped,
            warnings=self.warnings,
            notes=self.notes,
        )


def migrateLegacyConfig(
    old: dict[str, Any],
    deviceSchema: dict[str, dict[str, set[str]]],
) -> MigrationData:
    """Convert one legacy schema-4.1 profile to a sparse schema-5.0 profile.

    The output intentionally contains only deterministic migrated values.
    MW4 itself supplies defaults for v5-only settings when the profile is loaded.
    """
    version = str(old.get("version", ""))
    if version != SOURCE_PROFILE_VERSION:
        raise ValueError(
            f"Unsupported legacy profile version {version!r}; expected {SOURCE_PROFILE_VERSION}"
        )
    return LegacyMigrator(old, deviceSchema).run()
