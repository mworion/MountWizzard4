############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
satBaseUrl: str = "https://celestrak.org/NORAD/elements/gp.php?"  # SEC-5: changed http → https
satSourceURLs: dict[str, dict[str, str | bool]] = {
    "100 brightest": {
        "url": satBaseUrl + "GROUP=visual&FORMAT=json",
        "file": "visual.json",
        "unzip": False,
    },
    "Active": {
        "url": satBaseUrl + "GROUP=active&FORMAT=json",
        "file": "active.json",
        "unzip": False,
    },
    "Space Stations": {
        "url": satBaseUrl + "GROUP=stations&FORMAT=json",
        "file": "stations.json",
        "unzip": False,
    },
    "NOAA": {
        "url": satBaseUrl + "GROUP=noaa&FORMAT=json",
        "file": "noaa.json",
        "unzip": False,
    },
    "GEOS": {
        "url": satBaseUrl + "GROUP=geo&FORMAT=json",
        "file": "geos.json",
        "unzip": False,
    },
    "Weather": {
        "url": satBaseUrl + "GROUP=weather&FORMAT=json",
        "file": "weather.json",
        "unzip": False,
    },
    "Earth Resources": {
        "url": satBaseUrl + "GROUP=data&FORMAT=json",
        "file": "data.json",
        "unzip": False,
    },
    "TDRSS Tracking & Data Relay": {
        "url": satBaseUrl + "GROUP=tdrss&FORMAT=json",
        "file": "tdrss.json",
        "unzip": False,
    },
    "ARGOS": {
        "url": satBaseUrl + "GROUP=argos&FORMAT=json",
        "file": "argos.json",
        "unzip": False,
    },
    "Amateur Radio": {
        "url": satBaseUrl + "GROUP=amateur&FORMAT=json",
        "file": "amateur.json",
        "unzip": False,
    },
    "Space & Earth Science": {
        "url": satBaseUrl + "GROUP=science&FORMAT=json",
        "file": "science.json",
        "unzip": False,
    },
    "Engineering": {
        "url": satBaseUrl + "GROUP=engineering&FORMAT=json",
        "file": "engineering.json",
        "unzip": False,
    },
    "Last 30 days launch": {
        "url": satBaseUrl + "GROUP=last-30-days&FORMAT=json",
        "file": "tle-new.json",
        "unzip": False,
    },
    "Custom": {
        "url": "custom.txt",
        "file": "custom.txt",
        "unzip": False,
    },
}

mpcBaseUrl: str = "https://www.minorplanetcenter.net/Extended_Files/"
cometSourceURLs: dict[str, dict[str, str | bool]] = {
    "Comets Current": {
        "url": mpcBaseUrl + "cometels.json.gz",
        "file": "cometels.json",
        "unzip": True,
    },
}

asteroidSourceURLs: dict[str, dict[str, str | bool]] = {
    "Asteroids Daily": {
        "url": mpcBaseUrl + "nea_extended.json.gz",
        "file": "nea_extended.json",
        "unzip": True,
    },
    "Asteroids Near Earth Position": {
        "url": mpcBaseUrl + "nea_extended.json.gz",
        "file": "nea_extended.json",
        "unzip": True,
    },
    "Asteroids Potential Hazardous": {
        "url": mpcBaseUrl + "pha_extended.json.gz",
        "file": "pha_extended.json",
        "unzip": True,
    },
    "Asteroids TNO, Centaurus, SDO": {
        "url": mpcBaseUrl + "distant_extended.json.gz",
        "file": "distant_extended.json",
        "unzip": True,
    },
    "Asteroids Unusual e>0.5 or q>6 au": {
        "url": mpcBaseUrl + "unusual_extended.json.gz",
        "file": "unusual_extended.json",
        "unzip": True,
    },
}
