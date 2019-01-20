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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import subprocess
import time
import os
# external packages
from astropy.io import fits
# local imports


logger = logging.getLogger()


def convertToHMS(value):
    """

    :param value:
    :return: converted value as string
    """
    value = value.split('.')
    value = value[0].split(' ')
    value = f'{value[0]}:{value[1]}:{value[2]}'
    return value


def convertToDMS(value):
    """

    :param value:
    :return: converted value as string
    """
    value = value.split('.')
    value = value[0].split(' ')
    if int(value[0]) < 0:
        sign = '-'
    else:
        sign = '+'
    value = f'{sign}{value[0]}:{value[1]}:{value[2]}'
    return value


def readCheckFitsData(fitsPath):
    """

    :param fitsPath: fits file with image data
    :return: options as string for adding them to solve-field
    """

    with fits.open(fitsPath) as fitsHandle:
        fitsHeader = fitsHandle[0].header
        scale = fitsHeader.get('scale', '0')
        ra = fitsHeader.get('OBJCTRA', '')
        dec = fitsHeader.get('OBJCTDEC', '')
    ra = convertToHMS(ra)
    dec = convertToDMS(dec)
    scaleLow = float(scale) * 0.9
    scaleHigh = float(scale) * 1.1

    if scale == 0:
        return ''
    if not ra or not dec:
        return ''
    options = f' --scale-low {scaleLow} --scale-high {scaleHigh}'
    options += f' --ra {ra} --dec {dec} --radius 1'
    return options


def addWCSDataToFits(fitsPath='', wcsPath=''):
    """

    :param fitsPath: path to the fits file, where the wcs header should be embedded
    :param wcsPath: path to th fits file with wcs header
    :return: success
    """

    if not fitsPath or not wcsPath:
        return False

    with fits.open(fitsPath) as fitsHandle:
        fitsHeader = fitsHandle[0].header
        with fits.open(wcsPath) as wcsHandle:
            wcsHeader = wcsHandle[0].header
            for key, value in wcsHeader.items():
                if key.startswith('COMMENT'):
                    continue
                if key.startswith('HISTORY'):
                    continue
                fitsHeader[key] = value
    return True


def solve(binDir='', fitsPath='', dataDir='', solveOptions=''):
    """
    Solve uses the astrometry.net solver capabilities. The intention is to use an offline
    solving capability, so we need a installed instance. As we go multi platform and we
    need to focus on MW function, we use the astrometry.net package which is distributed
    with KStars / EKOS. Many thanks to them providing such a nice package.
    As we go using astrometry.net we focus on the minimum feature set possible to omit
    many of the installation and wrapping work to be done. So we only support solving of
    FITS files, use no python environment for astrometry.net parts (as we could access these
    via MW directly)

    The base outside ideas of implementation come from astrometry.net itself and the
    astrometry implementation from cloudmakers.eu (another nice package for MAC Astro
    software)

    We are using the following command line tools with options:

    image2xy:
        -O (overwriting file)
        -o <output filename>
        <fits file>

    solve-field:
        --overwrite
        --no-plots
        --no-remove-lines
        --no-verify-uniformize
        --sort-column FLUX  (sort for FLUX column)
        --uniformize 0  (disabling it)
        --config <config> (config file name, usually astrometry.cfg)
        xy (the output file from image2xy)


    :param binDir: directory with astrometry.net binaries
    :param fitsPath:  full path to fits file
    :param dataDir: directory for temp data
    :param solveOptions: option for solving
    :return: suc, coords, wcsHeader
    """
    baseOptions = ' --overwrite --no-plots --no-remove-lines --no-verify-uniformize'
    baseOptions += ' --uniformize 0 --sort-column FLUX --scale-units app'
    baseOptions += ' --crpix-center --cpulimit 60'

    command = binDir + 'image2xy'
    xyPath = dataDir + 'temp.xy'
    configPath = binDir + 'astrometry.cfg'
    solvedPath = dataDir + 'temp.solved'
    wcsPath = dataDir + 'temp.wcs'

    image2xyOptions = f' -O -o {xyPath} {fitsPath}'
    result = subprocess.getoutput(command + image2xyOptions)
    logger.debug('image2xy: ', result)
    if not result.startswith('simplexy: found'):
        return false, None, None

    extendedOptions = f' --config {configPath} {xyPath}'
    options = baseOptions + extendedOptions + solveOptions
    command = binDir + 'solve-field'

    result = subprocess.getoutput(command + options)
    logger.debug('solve-field: ', result)

    if os.path.isfile(solvedPath) and os.path.isfile(wcsPath):
        return True
    else:
        return False


if __name__ == "__main__":
    fitsFile = 'NGC7380.fits'
    # fitsFile = 'm51.fit'
    pathToCommandLine = '/Applications/kstars.app/Contents/MacOS/astrometry/bin/'
    pathToMW = '/Users/mw/PycharmProjects/MountWizzard4/'
    pathToData = pathToMW + 'data/'
    filePath_fits = pathToMW + fitsFile

    fitsOptions = readCheckFitsData(filePath_fits)

    result = solve(binDir=pathToCommandLine,
                   fitsPath=filePath_fits,
                   dataDir=pathToData,
                   solveOptions=fitsOptions)

    print(result)

    wcsPath = pathToData + 'temp.wcs'
    addWCSDataToFits(fitsPath=filePath_fits,
                     wcsPath=wcsPath)
