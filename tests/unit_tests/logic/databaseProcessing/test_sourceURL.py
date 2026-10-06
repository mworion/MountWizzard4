# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion


from mw4.logic.databaseProcessing.sourceURL import (
    asteroidSourceURLs,
    cometSourceURLs,
    satBaseUrl,
    satSourceURLs,
)

a = cometSourceURLs
b = satSourceURLs
c = asteroidSourceURLs
assert isinstance(a, dict)
assert isinstance(b, dict)
assert isinstance(c, dict)

# SEC-5: Celestrak base URL must use HTTPS
assert satBaseUrl.startswith("https://"), f"satBaseUrl must use https://, got: {satBaseUrl}"

# All satellite source URLs (except 'Custom') must also use HTTPS
for name, entry in satSourceURLs.items():
    url = entry["url"]
    if name != "Custom":
        assert url.startswith("https://"), (
            f"satSourceURLs['{name}']['url'] must use https://, got: {url}"
        )
