# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.logic.drivers.camera.cameraAlpacaAscomBase import CameraAlpacaAscomBase
from mw4.logic.drivers.frameworks.ascomClass import AscomClass


class CameraAscom(CameraAlpacaAscomBase, AscomClass):
    pass
