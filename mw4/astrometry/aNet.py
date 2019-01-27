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
import os
import platform
# external packages
from astropy.io import fits
# local imports


class Astrometry(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

        >>> astrometry = Astrometry(mwGlob=mwGlob,
        >>>                         )

    """

    __all__ = ['Astrometry',
               ]

    version = '0.31'
    logger = logging.getLogger(__name__)

    def __init__(self, mwGlob):
        self.mwGlob = mwGlob
        self.dataPath = self.mwGlob['dataDir']
        self.wcsPath = self.mwGlob['dataDir']

        if platform.system() == 'Darwin':
            self.binPath = '/Applications/kstars.app/Contents/MacOS/astrometry/bin'
            cfgPath = '/Users/mw/Library/Application Support/Astrometry'
        elif platform.system() == 'Linux':
            self.binPath = '/usr/bin'
            cfgPath = '/usr/share/astrometry'
        elif platform.system() == 'Windows':
            os.getenv('LOCALAPPDATA')
            self.binPath = ''
            cfgPath = '/usr/share/astrometry'

        cfgFile = self.dataPath + '/astrometry.cfg'
        with open(cfgFile, 'w+') as outFile:
            outFile.write('cpulimit 300\nadd_path {0}\nautoindex\n'.format(cfgPath))

    @staticmethod
    def convertToHMS(value):
        """

        :param value:
        :return: converted value as string
        """
        value = value.split('.')
        value = value[0].split(' ')
        value = f'{value[0]}:{value[1]}:{value[2]}'
        return value

    @staticmethod
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

    def readCheckFitsData(self, fitsPath='', optionalScale=0):
        """
        readCheckFitsData reads the fits file with the image and tries to get some key
        fields out of the header for preparing the solver. necessary data are

            - 'SCALE': pixel scale in arcsec per pixel
            - 'OBJCTRA' : ra position of the object in HMS format
            - 'OBJCTDEC' : dec position of the object in DMS format

        if OBJCTRA / OBJCTDEC is not readable or not present, we remove the parameters
        to get a blind solve

        :param fitsPath: fits file with image data
        :param optionalScale: optional scaling used, when not scale parameter is in header
        :return: options as string
        """

        if not fitsPath:
            return ''

        with fits.open(fitsPath) as fitsHandle:
            fitsHeader = fitsHandle[0].header
            scale = fitsHeader.get('scale', '0')
            ra = fitsHeader.get('OBJCTRA', '')
            dec = fitsHeader.get('OBJCTDEC', '')

        if scale == 0:
            scale = optionalScale
        ra = self.convertToHMS(ra)
        dec = self.convertToDMS(dec)
        scaleLow = float(scale) * 0.9
        scaleHigh = float(scale) * 1.1

        if not ra or not dec:
            return ''
        options = f' --scale-low {scaleLow} --scale-high {scaleHigh}'
        options += f' --ra {ra} --dec {dec} --radius 1'
        return options

    def addWCSDataToFits(self, fitsPath=''):
        """
        addWCSDataToFits reads the fits file containing the wcs data output from solve-field
        and embeds it to the given fits file with image

        :param fitsPath: path to the fits file, where the wcs header should be embedded
        :return: success
        """

        if not fitsPath:
            return False

        wcsFile = self.wcsPath + '/temp.wcs'
        with fits.open(fitsPath) as fitsHandle:
            fitsHeader = fitsHandle[0].header
            with fits.open(wcsFile) as wcsHandle:
                wcsHeader = wcsHandle[0].header
                for key, value in wcsHeader.items():
                    if key.startswith('COMMENT'):
                        continue
                    if key.startswith('HISTORY'):
                        continue
                    fitsHeader[key] = value
        return True

    def solve(self, fitsPath='', solveOptions=''):
        """
        Solve uses the astrometry.net solver capabilities. The intention is to use an
        offline solving capability, so we need a installed instance. As we go multi
        platform and we need to focus on MW function, we use the astrometry.net package
        which is distributed with KStars / EKOS. Many thanks to them providing such a
        nice package.
        As we go using astrometry.net we focus on the minimum feature set possible to
        omit many of the installation and wrapping work to be done. So we only support
        solving of FITS files, use no python environment for astrometry.net parts (as we
        could access these via MW directly)

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


        :param fitsPath:  full path to fits file
        :param solveOptions: option for solving
        :return: suc, coords, wcsHeader
        """
        baseOptions = ' --overwrite --no-plots --no-remove-lines --no-verify-uniformize'
        baseOptions += ' --uniformize 0 --sort-column FLUX --scale-units app'
        baseOptions += ' --crpix-center --cpulimit 60'

        command = self.binPath + '/image2xy'
        xyPath = self.dataPath + '/temp.xy'
        configPath = self.dataPath + '/astrometry.cfg'
        solvedPath = self.dataPath + '/temp.solved'
        wcsPath = self.dataPath + '/temp.wcs'

        image2xyOptions = f' -O -o {xyPath} {fitsPath}'
        result = subprocess.getoutput(command + image2xyOptions)
        self.logger.debug('image2xy: ', result)
        if not result.startswith('simplexy: found'):
            return False

        extendedOptions = f' --config {configPath} {xyPath}'
        options = baseOptions + extendedOptions + solveOptions
        command = self.binPath + '/solve-field'

        result = subprocess.getoutput(command + options)
        self.logger.debug('solve-field: ', result)

        if os.path.isfile(solvedPath) and os.path.isfile(wcsPath):
            return True
        else:
            return False


if __name__ == "__main__":
    fitsFile = '/NGC7380.fits'
    # fitsFile = '/m51.fit'
    mwGlob = {'workDir': '.',
              'configDir': './config',
              'dataDir': './data',
              'modeldata': 'test',
              }

    astrometry = Astrometry(mwGlob)
    pathToMW = '/Users/mw/PycharmProjects/MountWizzard4'
    dataPath = pathToMW + 'data'
    fitsPath = pathToMW + fitsFile

    fitsOptions = astrometry.readCheckFitsData(fitsPath=fitsPath)

    result = astrometry.solve(fitsPath=fitsPath,
                              solveOptions=fitsOptions)

    astrometry.addWCSDataToFits(fitsPath=fitsPath)
    print(result)
