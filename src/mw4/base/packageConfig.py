# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from typing import Final

# Feature flags - set once at import time; never mutated at runtime.
isAnalyse: Final[bool] = False
isReference: Final[bool] = False
