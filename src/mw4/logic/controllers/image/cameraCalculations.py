# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from typing import Any


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
