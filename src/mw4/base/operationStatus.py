# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from enum import IntEnum


class OperationStatus(IntEnum):
    IDLE = 0
    MODEL_BATCH = 1
    MODEL_FILE = 2
    MODEL_SYNC = 3
    MODEL_ITERATIVE = 4
    EXPOSE_1 = 5
    EXPOSE_N = 6
    SOLVE = 7
