# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.mountcontrol.mountStatus import STATUS_LABELS, MountStatus

CODES = {
    0: "TRACKING",
    1: "STOPPED",
    2: "SLEWING_TO_PARK",
    3: "UNPARKING",
    4: "SLEWING_TO_HOME",
    5: "PARKED",
    6: "SLEWING",
    7: "TRACKING_OFF",
    8: "MOTOR_LOW_TEMP",
    9: "TRACKING_OUTSIDE_LIMITS",
    10: "FOLLOWING_SATELLITE",
    11: "USER_OK_NEEDED",
    98: "UNKNOWN",
    99: "ERROR",
}


def test_mountStatus_codes():
    assert {int(s): s.name for s in MountStatus} == CODES


def test_mountStatus_labelsCoverAllCodes():
    assert set(STATUS_LABELS) == set(MountStatus)


def test_mountStatus_labelsUnique():
    labels = list(STATUS_LABELS.values())
    assert len(labels) == len(set(labels))
    assert all(isinstance(label, str) and label for label in labels)


def test_mountStatus_intComparison():
    assert MountStatus.TRACKING == 0
    assert MountStatus.ERROR == 99
