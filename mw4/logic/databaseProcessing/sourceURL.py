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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local import

satBaseUrl = 'http://www.celestrak.org/NORAD/elements/gp.php?'
satSourceURLs = {
    '100 brightest': {
        'url': satBaseUrl + 'GROUP=visual&FORMAT=tle',
        'file': 'visual.txt'
    },
    'Active': {
        'url': satBaseUrl + 'GROUP=active&FORMAT=tle',
        'file': 'active.txt'
    },
    'Space Stations': {
        'url': satBaseUrl + 'GROUP=stations&FORMAT=tle',
        'file': 'stations.txt'
    },
    'NOAA': {
        'url': satBaseUrl + 'GROUP=noaa&FORMAT=tle',
        'file': 'noaa.txt'
    },
    'GEOS': {
        'url': satBaseUrl + 'GROUP=geo&FORMAT=tle',
        'file': 'geos.txt'
    },
    'Weather': {
        'url': satBaseUrl + 'GROUP=weather&FORMAT=tle',
        'file': 'weather.txt'
    },
    'Earth Resources': {
        'url': satBaseUrl + 'GROUP=resource&FORMAT=tle',
        'file': 'resource.txt'
    },
    'TDRSS Tracking & Data Relay': {
        'url': satBaseUrl + 'GROUP=tdrss&FORMAT=tle',
        'file': 'tdrss.txt'
    },
    'ARGOS': {
        'url': satBaseUrl + 'GROUP=argos&FORMAT=tle',
        'file': 'argos.txt'
    },
    'Amateur Radio': {
        'url': satBaseUrl + 'GROUP=amateur&FORMAT=tle',
        'file': 'amateur.txt'
    },
    'Space & Earth Science': {
        'url': satBaseUrl + 'GROUP=science&FORMAT=tle',
        'file': 'science.txt'
    },
    'Engineering': {
        'url': satBaseUrl + 'GROUP=engineering&FORMAT=tle',
        'file': 'engineering.txt'
    },
    'Last 30 days launch': {
        'url': satBaseUrl + 'GROUP=last-30-days&FORMAT=tle',
        'file': 'tle-new.txt'
    },
    'Custom': {
        'url': 'custom.txt',
        'file': 'custom.txt'
    },
}

mpcBaseUrl = 'https://www.minorplanetcenter.net/Extended_Files/'
cometSourceURLs = {
    'Comets Current':
        {
            'url': mpcBaseUrl + 'cometels.json.gz',
            'file': 'cometels.json.gz',
         },
    }

asteroidSourceURLs = {
    'Asteroids Daily':
        {
            'url': mpcBaseUrl + 'nea_extended.json.gz',
            'file': 'nea_extended.json.gz',
         },
    'Asteroids Near Earth Position':
        {
            'url': mpcBaseUrl + 'nea_extended.json.gz',
            'file': 'nea_extended.json.gz',
         },
    'Asteroids Potential Hazardous':
        {
            'url': mpcBaseUrl + 'pha_extended.json.gz',
            'file': 'pha_extended.json.gz',
         },
    'Asteroids TNO, Centaurus, SDO':
        {
            'url': mpcBaseUrl + 'distant_extended.json.gz',
            'file': 'distant_extended.json.gz',
         },
    'Asteroids Unusual e>0.5 or q>6 au':
        {
            'url': mpcBaseUrl + 'unusual_extended.json.gz',
            'file': 'unusual_extended.json.gz',
        },
    'Asteroids MPC5000 (large! >100 MB)':
        {
            'url': mpcBaseUrl + 'mpcorb_extended.json.gz',
            'file': 'mpcorb_extended.json.gz',
        },
}
