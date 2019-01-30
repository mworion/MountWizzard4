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
import glob
import platform
# external packages
from astropy.io import fits
# local imports


class Astrometry(object):
    """
    the class Astrometry inherits all information and handling of astrometry.net handling

        >>> astrometry = Astrometry(tempDir=tempDir,
        >>>                         )

    """

    __all__ = ['Astrometry',
               ]

    version = '0.31'
    logger = logging.getLogger(__name__)

    def __init__(self, tempDir):
        self.tempDir = tempDir

        if platform.system() == 'Darwin':
            binPath = '/Applications/kstars.app/Contents/MacOS/astrometry/bin'
            self.binPathSolveField = binPath + '/solve-field'
            self.binPathImage2xy = binPath + '/image2xy'
            self.indexPath = '/Users/mw/Library/Application Support/Astrometry'
        elif platform.system() == 'Linux':
            binPath = '/usr/bin'
            self.binPathSolveField = binPath + '/solve-field'
            self.binPathImage2xy = binPath + '/image2xy'
            self.indexPath = '/usr/share/astrometry'
        elif platform.system() == 'Windows':
            base = os.getenv('LOCALAPPDATA').replace('\\', '/')
            binPath = base + '/cygwin_ansvr/lib/astrometry/bin'
            self.runPath = base + '/run'
            self.binPathSolveField = binPath + '/solve-field.exe'
            self.binPathImage2xy = binPath + '/image2xy.exe'
            self.indexPath = base + '/cygwin_ansvr/usr/share/astrometry/data'
            # os.environ['COMSPEC'] = 'C:\\Windows\\system32\\cmd.exe'

        cfgFile = self.tempDir + '/astrometry.cfg'
        with open(cfgFile, 'w+') as outFile:
            outFile.write('cpulimit 300\nadd_path {0}\nautoindex\n'.format(self.indexPath))

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

    def checkAvailability(self):
        """

        :return: True if local solve and components is available
        """

        if not os.path.isfile(self.binPathSolveField):
            self.logger.error(f'{self.binPathSolveField} not found')
            return False
        if not os.path.isfile(self.binPathImage2xy):
            self.logger.error(f'{self.binPathImage2xy} not found')
            return False
        if not glob.glob(self.indexPath + '/index-4*.fits'):
            self.logger.error('no index files found')
            return False
        self.logger.info('solve-field, image2xy and index files available')
        return True

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

        wcsFile = self.tempDir + '/temp.wcs'
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

        xyPath = self.tempDir + '/temp.xy'
        configPath = self.tempDir + '/astrometry.cfg'
        solvedPath = self.tempDir + '/temp.solved'
        wcsPath = self.tempDir + '/temp.wcs'

        runnable = [self.binPathImage2xy,
                    '-O',
                    '-o',
                    xyPath,
                    fitsPath]
        if platform.system() == 'Windows':
            runnable.insert(0, self.runPath)
        result = subprocess.run(runnable,
                                stdout=False,
                                shell=True,
                                )

        self.logger.debug('image2xy: ', result)
        if result.returncode:
            return False

        runnable = [self.binPathSolveField,
                    '--overwrite',
                    '--no-plots',
                    '--no-remove-lines',
                    '--no-verify-uniformize',
                    '--overwrite',
                    '--no-plots',
                    '--no-remove-lines',
                    '--no-verify-uniformize',
                    '--uniformize', '0',
                    '--sort-column', 'FLUX',
                    '--scale-units', 'app',
                    '--crpix-center',
                    '--cpulimit', '60',
                    '--config',
                    configPath,
                    xyPath,
                    ]
        if platform.system() == 'Windows':
            runnable.insert(0, self.runPath)
        if solveOptions:
            runnable.append(solveOptions.split())
        result = subprocess.run(runnable,
                                stdout=False)

        self.logger.debug('solve-field: ', result)
        if result.returncode:
            return False

        if os.path.isfile(solvedPath) and os.path.isfile(wcsPath):
            return True
        else:
            return False


if __name__ == "__main__":
    fitsFile = 'NGC7380.fits'
    # fitsFile = 'm51.fit'
    workDir = os.getcwd().replace('\\', '/')
    tempDir = workDir + '/data'

    astrometry = Astrometry(tempDir=tempDir)

    fitsPath = workDir + '/' + fitsFile

    print(astrometry.checkAvailability())
    fitsOptions = astrometry.readCheckFitsData(fitsPath=fitsPath)
    result = astrometry.solve(fitsPath=fitsPath,
                              solveOptions=fitsOptions)

    astrometry.addWCSDataToFits(fitsPath=fitsPath)
    print(result)
