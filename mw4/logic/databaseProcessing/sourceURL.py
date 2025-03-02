############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import

satBaseUrl = "http://www.celestrak.org/NORAD/elements/gp.php?"
satSourceURLs = {
    "100 brightest": {
        "url": satBaseUrl + "GROUP=visual&FORMAT=tle",
        "file": "visual.txt",
        "unzip": False,
    },
    "Active": {
        "url": satBaseUrl + "GROUP=active&FORMAT=tle",
        "file": "active.txt",
        "unzip": False,
    },
    "Space Stations": {
        "url": satBaseUrl + "GROUP=stations&FORMAT=tle",
        "file": "stations.txt",
        "unzip": False,
    },
    "NOAA": {
        "url": satBaseUrl + "GROUP=noaa&FORMAT=tle",
        "file": "noaa.txt",
        "unzip": False,
    },
    "GEOS": {
        "url": satBaseUrl + "GROUP=geo&FORMAT=tle",
        "file": "geos.txt",
        "unzip": False,
    },
    "Weather": {
        "url": satBaseUrl + "GROUP=weather&FORMAT=tle",
        "file": "weather.txt",
        "unzip": False,
    },
    "Earth Resources": {
        "url": satBaseUrl + "GROUP=resource&FORMAT=tle",
        "file": "resource.txt",
        "unzip": False,
    },
    "TDRSS Tracking & Data Relay": {
        "url": satBaseUrl + "GROUP=tdrss&FORMAT=tle",
        "file": "tdrss.txt",
        "unzip": False,
    },
    "ARGOS": {
        "url": satBaseUrl + "GROUP=argos&FORMAT=tle",
        "file": "argos.txt",
        "unzip": False,
    },
    "Amateur Radio": {
        "url": satBaseUrl + "GROUP=amateur&FORMAT=tle",
        "file": "amateur.txt",
        "unzip": False,
    },
    "Space & Earth Science": {
        "url": satBaseUrl + "GROUP=science&FORMAT=tle",
        "file": "science.txt",
        "unzip": False,
    },
    "Engineering": {
        "url": satBaseUrl + "GROUP=engineering&FORMAT=tle",
        "file": "engineering.txt",
        "unzip": False,
    },
    "Last 30 days launch": {
        "url": satBaseUrl + "GROUP=last-30-days&FORMAT=tle",
        "file": "tle-new.txt",
        "unzip": False,
    },
    "Custom": {
        "url": "custom.txt",
        "file": "custom.txt",
        "unzip": False,
    },
}

mpcBaseUrl = "https://www.minorplanetcenter.net/Extended_Files/"
cometSourceURLs = {
    "Comets Current": {
        "url": mpcBaseUrl + "cometels.json.gz",
        "file": "cometels.json",
        "unzip": True,
    },
}

asteroidSourceURLs = {
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
