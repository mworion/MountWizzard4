# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from mw4.mountcontrol.connection import Connection
from packaging.version import InvalidVersion, Version
from typing import Any


class Firmware:
    log = logging.getLogger("MW4")

    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self.product: str = ""
        self._vString: Version = Version("0.0.0")
        self.hardware: str = ""
        self.date: str = ""
        self.time: str = ""

    @property
    def vString(self) -> str:
        return self._vString.public

    @vString.setter
    def vString(self, value: str) -> None:
        self._vString = Version(value)

    def checkNewer(self, compare: str) -> bool:
        return self._vString >= Version(compare)

    def isHW2024(self) -> bool:
        return self.hardware == "Q-TYPE2024"

    def isHW2012(self) -> bool:
        return self.hardware == "Q-TYPE2012"

    def parse(self, response: list, numberOfChunks: int) -> bool:
        if len(response) != numberOfChunks:
            self.log.warning("wrong number of chunks")
            return False
        try:
            self.vString = response[1]
        except InvalidVersion:
            self.log.warning(f"Invalid firmware version: [{response}]")
            return False
        self.date = response[0]
        self.product = response[2]
        self.time = response[3]
        self.hardware = response[4]
        return True

    def poll(self) -> bool:
        conn = Connection(self.parent)
        commandString = ":GVD#:GVN#:GVP#:GVT#:GVZ#"
        suc, response, chunks = conn.communicate(commandString)
        if not suc:
            return False
        return self.parse(response, chunks)
