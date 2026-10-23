# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass, field
from mw4.base.cameraKeys import (
    CCD_GAIN_GAIN,
    CCD_INFO_CCD_MAX_X,
    CCD_OFFSET_OFFSET,
    CCD_TEMPERATURE_CCD_TEMPERATURE_VALUE,
)
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
        hasCooler=CCD_TEMPERATURE_CCD_TEMPERATURE_VALUE in data,
        hasGain=CCD_GAIN_GAIN in data,
        hasOffset=CCD_OFFSET_OFFSET in data,
        hasSensor=CCD_INFO_CCD_MAX_X in data,
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


def switchPairState(value: Any) -> tuple[bool, bool]:
    """returns the run state of an (on, off) button pair for a truthy / None / falsy value."""
    if value:
        return True, False
    if value is None:
        return False, False
    return False, True


def strictPairState(value: Any) -> tuple[bool, bool]:
    """returns the run state of an (open, close) button pair, only True / False count."""
    if value is True:
        return True, False
    if value is False:
        return False, True
    return False, False


def filterNames(data: dict[str, Any]) -> list[str]:
    """returns the filter names in the order of the device data."""
    return [data[key] for key in data if "FILTER_NAME.FILTER_SLOT_NAME_" in key]


def filterNumberForName(data: dict[str, Any], name: str) -> int:
    """returns the slot number of a filter name; alpaca counts slots from 0, indi from 1."""
    index = filterNames(data).index(name)
    return index if "FILTER_NAME.FILTER_SLOT_NAME_0" in data else index + 1


DomeTurn = Literal["ccw", "cw", "abort"]
DomeShutter = Literal["open", "close"]


def hidDomeAction(turnVal: int, openVal: int) -> tuple[DomeTurn, DomeShutter | None]:
    """maps the hid controller values (0..255) to a dome turn and shutter action."""
    turn: DomeTurn = "ccw" if turnVal < 64 else "cw" if turnVal > 192 else "abort"
    shutter: DomeShutter | None = "open" if openVal < 64 else "close" if openVal > 192 else None
    return turn, shutter
