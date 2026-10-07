# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from enum import IntEnum


class MountStatus(IntEnum):
    """Numeric status codes reported by the 10micron mount.

    Defined as an :class:`IntEnum` so existing integer comparisons keep
    working while consumers can refer to symbolic names. The human-readable
    label associated with each code lives in :data:`STATUS_LABELS` and is
    the single source of truth for both the valid-code set and the textual
    descriptions exposed through :class:`ObsSite`.
    """

    TRACKING = 0
    STOPPED = 1
    SLEWING_TO_PARK = 2
    UNPARKING = 3
    SLEWING_TO_HOME = 4
    PARKED = 5
    SLEWING = 6
    TRACKING_OFF = 7
    MOTOR_LOW_TEMP = 8
    TRACKING_OUTSIDE_LIMITS = 9
    FOLLOWING_SATELLITE = 10
    USER_OK_NEEDED = 11
    UNKNOWN = 98
    ERROR = 99


# Single source of truth for the mount status codes and their human-readable
# labels. The valid-code set and the legacy ``STAT`` mapping used by the GUI
# are derived from this dictionary so a new status only needs to be added in
# one place (plus the :class:`MountStatus` enum above).
STATUS_LABELS: dict[MountStatus, str] = {
    MountStatus.TRACKING: "tracking",
    MountStatus.STOPPED: "stopped after STOP",
    MountStatus.SLEWING_TO_PARK: "slewing park position",
    MountStatus.UNPARKING: "unparking",
    MountStatus.SLEWING_TO_HOME: "slewing home position",
    MountStatus.PARKED: "parked",
    MountStatus.SLEWING: "slewing / going to stop",
    MountStatus.TRACKING_OFF: "tracking Off",
    MountStatus.MOTOR_LOW_TEMP: "motor low temperature",
    MountStatus.TRACKING_OUTSIDE_LIMITS: "tracking outside limits",
    MountStatus.FOLLOWING_SATELLITE: "following satellite",
    MountStatus.USER_OK_NEEDED: "user OK needed",
    MountStatus.UNKNOWN: "unknown status",
    MountStatus.ERROR: "error",
}
