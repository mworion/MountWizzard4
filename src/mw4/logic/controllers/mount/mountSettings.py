# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SettingSpec:
    """describes one mount setting: dialog texts, bounds and the setter to call."""

    title: str
    label: str
    setterName: str
    attribute: str = ""
    errorLabel: str = ""
    prompt: str = ""
    minVal: float = 0
    maxVal: float = 0
    step: float = 1
    isInt: bool = True
    minAttribute: str = ""
    maxAttribute: str = ""


SWITCHES: dict[str, SettingSpec] = {
    "unattendedFlip": SettingSpec(
        title="Set Unattended Flip",
        label="Unattended flip",
        setterName="setUnattendedFlip",
    ),
    "webInterface": SettingSpec(
        title="Set Web Interface",
        label="Web Interface",
        setterName="setWebInterface",
    ),
    "dualAxisTracking": SettingSpec(
        title="Set Dual Axis Tracking",
        label="DualAxis tracking",
        setterName="setDualAxisTracking",
    ),
    "wol": SettingSpec(
        title="Set Wake On Lan",
        label="Wake On Lan",
        setterName="setWOL",
        attribute="wakeOnLan",
    ),
    "apo": SettingSpec(
        title="Set Auto Power On",
        label="AutoPowerOn",
        setterName="setAutoPower",
        attribute="autoPowerOn",
    ),
    "refraction": SettingSpec(
        title="Set Refraction Correction",
        label="Refraction corr",
        errorLabel="Refraction correction",
        setterName="setRefraction",
    ),
}

VALUES: dict[str, SettingSpec] = {
    "meridianTrack": SettingSpec(
        title="Set Meridian Limit Track",
        label="Meridian Lim Track",
        errorLabel="Meridian Limit Track",
        setterName="setMeridianLimitTrack",
        attribute="meridianLimitTrack",
        prompt="Value (1-30):",
        minVal=1,
        maxVal=30,
    ),
    "meridianSlew": SettingSpec(
        title="Set Meridian Limit Slew",
        label="Meridian Lim Slew",
        errorLabel="Meridian Limit Slew",
        setterName="setMeridianLimitSlew",
        attribute="meridianLimitSlew",
        prompt="Value (0-30):",
        minVal=0,
        maxVal=30,
    ),
    "horizonHigh": SettingSpec(
        title="Set Horizon Limit High",
        label="Horizon Limit High",
        setterName="setHorizonLimitHigh",
        attribute="horizonLimitHigh",
        prompt="Value (0-90):",
        minVal=0,
        maxVal=90,
    ),
    "horizonLow": SettingSpec(
        title="Set Horizon Limit Low",
        label="Horizon Limit Low",
        setterName="setHorizonLimitLow",
        attribute="horizonLimitLow",
        prompt="Value (-5 - 90):",
        minVal=-5,
        maxVal=90,
    ),
    "slewRate": SettingSpec(
        title="Set Slew Rate",
        label="Slew Rate",
        setterName="setSlewRate",
        attribute="slewRate",
        minAttribute="slewRateMin",
        maxAttribute="slewRateMax",
    ),
    "refractionTemp": SettingSpec(
        title="Set Refraction Temperature",
        label="Refraction Temp",
        setterName="setRefractionTemp",
        attribute="refractionTemp",
        prompt="Value (-40...75):",
        minVal=-40,
        maxVal=75,
        isInt=False,
    ),
    "refractionPress": SettingSpec(
        title="Set Refraction Pressure",
        label="Refraction Press",
        setterName="setRefractionPress",
        attribute="refractionPress",
        prompt="Value (500...1300):",
        minVal=500,
        maxVal=1300,
        isInt=False,
    ),
    "settleTime": SettingSpec(
        title="Set Settle Time",
        label="Settle Time",
        setterName="setSettleTime",
        attribute="settleTime",
        prompt="Value (0-999):",
        minVal=0,
        maxVal=999,
    ),
}


class MountSettingsController:
    """applies mount settings and reports the result, without any GUI dependency."""

    def __init__(self, setting: Any, notify: Callable[[int, str, str, str], Any]) -> None:
        self.setting = setting
        self.notify = notify

    def currentValue(self, spec: SettingSpec) -> float:
        """returns the actual setting value, 0 if the mount did not report one."""
        value = getattr(self.setting, spec.attribute)
        if value is None:
            return 0
        return int(value) if spec.isInt else value

    def valueRange(self, spec: SettingSpec) -> tuple[float, float, str]:
        """returns minimum, maximum and the dialog prompt for a value setting."""
        if not spec.minAttribute:
            return spec.minVal, spec.maxVal, spec.prompt
        minVal = getattr(self.setting, spec.minAttribute)
        maxVal = getattr(self.setting, spec.maxAttribute)
        minVal = 0 if minVal is None else int(minVal)
        maxVal = 0 if maxVal is None else int(maxVal)
        return minVal, maxVal, f"Value ({minVal}...{maxVal}):"

    def switchIndex(self, spec: SettingSpec) -> int:
        """returns the preselected index of the ON / OFF list."""
        if not spec.attribute:
            return 0
        return 0 if getattr(self.setting, spec.attribute) == "ON" else 1

    def applySwitch(self, spec: SettingSpec, value: str) -> bool:
        """sets a switch setting; value is the dialog text ON or OFF."""
        suc = getattr(self.setting, spec.setterName)(value == "ON")
        self.report(spec, suc, value)
        return suc

    def applyValue(self, spec: SettingSpec, value: float) -> bool:
        """sets a numeric setting."""
        suc = getattr(self.setting, spec.setterName)(value)
        self.report(spec, suc, value)
        return suc

    def report(self, spec: SettingSpec, suc: bool, value: Any) -> None:
        if suc:
            self.notify(0, "Mount", "Setting", f"{spec.label}: [{value}]")
        else:
            label = spec.errorLabel or spec.label
            self.notify(2, "Mount", "Setting", f"{label} cannot be set")
