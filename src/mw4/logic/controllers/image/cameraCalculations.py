# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class RangeSpec:
    """how a camera value (gain, offset) can be chosen: from a list, in a range or free."""

    kind: Literal["list", "range", "free"]
    values: list[Any] = field(default_factory=list)
    minVal: int = 0
    maxVal: int = 0
    step: int = 1


def describeRange(data: dict[str, Any], prefix: str) -> RangeSpec:
    """reads the list or min / max limits for keys like CCD_GAIN.GAIN_LIST / _MIN / _MAX."""
    entries = data.get(f"{prefix}_LIST")
    if entries is not None:
        return RangeSpec(kind="list", values=list(entries))
    minVal = data.get(f"{prefix}_MIN")
    maxVal = data.get(f"{prefix}_MAX")
    if minVal is not None and maxVal is not None:
        minVal, maxVal = int(minVal), int(maxVal)
        step = int((maxVal - minVal) / 20)
        return RangeSpec(kind="range", minVal=minVal, maxVal=maxVal, step=step)
    return RangeSpec(kind="free")


@dataclass(frozen=True)
class CameraCapabilities:
    hasCooler: bool
    hasGain: bool
    hasOffset: bool
    hasSensor: bool


def cameraCapabilities(data: dict[str, Any]) -> CameraCapabilities:
    """derives which camera function groups are available from the driver data."""
    return CameraCapabilities(
        hasCooler="CCD_TEMPERATURE.CCD_TEMPERATURE_VALUE" in data,
        hasGain="CCD_GAIN.GAIN" in data,
        hasOffset="CCD_OFFSET.OFFSET" in data,
        hasSensor="CCD_INFO.CCD_MAX_X" in data,
    )


def optimalBinning(pixelX: float, pixelY: float) -> int:
    """returns the binning that brings the sensor close to 1750 pixel."""
    return max(1, min(int(pixelX / 1750), int(pixelY / 1750)))


def pickListEntry(index: int, entries: list[Any]) -> Any:
    """returns the 1-based indexed entry; an index beyond the list selects the last one."""
    index = min(max(index, 0), len(entries))
    return entries[index - 1]


def filterSlotRange(data: dict[str, Any]) -> tuple[int, int]:
    """returns first and last filter slot; alpaca counts slots from 0, indi from 1."""
    numberFilter = len([key for key in data if "FILTER_NAME.FILTER_SLOT_NAME_" in key])
    if "FILTER_NAME.FILTER_SLOT_NAME_0" in data:
        return 0, numberFilter - 1
    return 1, numberFilter
