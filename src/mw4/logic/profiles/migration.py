# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from collections.abc import Callable
from mw4.logic.profiles.config import profileVersion
from typing import Any

log: logging.Logger = logging.getLogger("MW4")

# maps a profile version to the function converting it to the next version;
# each function must return the dict with the new "version" set
migrations: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}


def migrateConfig(data: dict[str, Any]) -> dict[str, Any] | None:
    """Bring a raw profile dict to the current version, None if not possible."""
    version = data.get("version", "")
    while version != profileVersion:
        migrate = migrations.get(version)
        if migrate is None:
            return None
        log.info("Migrating profile from version %s", version)
        data = migrate(data)
        newVersion = data.get("version", "")
        if newVersion == version:
            return None
        version = newVersion
    return data
