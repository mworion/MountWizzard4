# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from __future__ import annotations

from mw4.mountcontrol.convert import stringToAngle, valueToAngle
from skyfield.api import Angle
from typing import Any, Literal, overload


class AngleProperty:
    """Data descriptor for an Angle attribute stored as ``_<name>``.

    Angle instances are stored unchanged, any other input is converted with
    ``valueToAngle`` (parser "value", numeric / mount values) or
    ``stringToAngle`` (parser "string", sexagesimal text input).
    """

    def __init__(
        self,
        preference: Literal["hours", "degrees"],
        parser: Literal["value", "string"] = "value",
    ) -> None:
        self.preference = preference
        self.convert = valueToAngle if parser == "value" else stringToAngle
        self.name = ""
        self.attr = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.attr = f"_{name}"

    @overload
    def __get__(self, obj: None, owner: type) -> AngleProperty: ...

    @overload
    def __get__(self, obj: object, owner: type) -> Angle: ...

    def __get__(self, obj: object | None, owner: type) -> AngleProperty | Angle:
        if obj is None:
            return self
        return getattr(obj, self.attr)

    def __set__(self, obj: object, value: Any) -> None:
        if not isinstance(value, Angle):
            value = self.convert(value, preference=self.preference)
        setattr(obj, self.attr, value)
