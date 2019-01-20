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
'''
image2xy options:
Usage: image2xy [options] fitsname.fits 

Read a FITS file, find objects, and write out 
X, Y, FLUX to   fitsname.xy.fits .

   [-e <extension>]: read from a single FITS extension
   [-O]  overwrite existing output file.
   [-o <output-filename>]  write XYlist to given filename.
   [-L <Lanczos-order>]
   [-8]  don't use optimization for byte (u8) images.
   [-H]  downsample by a factor of 2 before running simplexy.
   [-d <downsample-factor>]  downsample by an integer factor before running simplexy.
   [-D <downsample-factor>] downsample, if necessary, by this many factors of two.
   [-s <median-filtering scale>]: set median-filter box size (default 100 pixels)
   [-w <PSF width>]: set Gaussian PSF sigma (default 1 pixel)
   [-g <sigma>]: set image noise level
   [-p <sigmas>]: set significance level of peaks (default 8 sigmas)
   [-a <saddle-sigmas>]: set "saddle" level joining peaks (default 5 sigmas)
   [-P <image plane>]: pull out a single plane of a multi-color image (default: first plane)
   [-b]: don't do (median-based) background subtraction
   [-G <background>]: subtract this 'global' background value; implies -b
   [-m]: set maximum extended object size for deblending (default 2000 pixels)

   [-S <background-subtracted image>]: save background-subtracted image to this filename (FITS float image)
   [-B <background image>]: save background image to filename
   [-U <smoothed background-subtracted image>]: save smoothed background-subtracted image to filename
   [-M <mask image>]: save mask image to filename
   [-C <blob-image>]: save connected-components image to filename

   [-v] verbose - repeat for more and more verboseness

   image2xy 'file.fits[1]'   - process first extension.
   image2xy 'file.fits[2]'   - process second extension 
   image2xy file.fits+2      - same as above 

solve-field is an upper layer api for using solving astro images. 

Option for solve-field:

  -h / --help: print this help message
  -v / --verbose: be more chatty -- repeat for even more verboseness
  -D / --dir <directory>: place all output files in the specified directory
  -o / --out <base-filename>: name the output files with this base name
  -b / --backend-config <filename>: use this config file for the
          "astrometry-engine" program
  --config <filename>: use this config file for the "astrometry-engine" program
  --batch: run astrometry-engine once, rather than once per input file
  -f / --files-on-stdin: read filenames to solve on stdin, one per line
  -p / --no-plots: don't create any plots of the results
  --plot-scale <scale>: scale the plots by this factor (eg, 0.25)
  --plot-bg <filename (JPEG)>: set the background image to use for plots
  -G / --use-wget: use wget instead of curl
  -O / --overwrite: overwrite output files if they already exist
  -K / --continue: don't overwrite output files if they already exist; continue
          a previous run
  -J / --skip-solved: skip input files for which the 'solved' output file
          already exists; NOTE: this assumes single-field input files
  --fits-image: assume the input files are FITS images
  -N / --new-fits <filename>: output filename of the new FITS file containing
          the WCS header; "none" to not create this file
  -Z / --kmz <filename>: create KMZ file for Google Sky.  (requires wcs2kml)
  -i / --scamp <filename>: create image object catalog for SCAMP
  -n / --scamp-config <filename>: create SCAMP config file snippet
  -U / --index-xyls <filename>: output filename for xylist containing the image
          coordinate of stars from the index
  --just-augment: just write the augmented xylist files; don't run
          astrometry-engine.
  --axy <filename>: output filename for augment xy list (axy)
  --temp-axy: write 'augmented xy list' (axy) file to a temp file
  --timestamp: add timestamps to log messages
  -7 / --no-delete-temp: don't delete temp files (for debugging)

  -L / --scale-low <scale>: lower bound of image scale estimate
  -H / --scale-high <scale>: upper bound of image scale estimate
  -u / --scale-units <units>: in what units are the lower and upper bounds?
     choices:  "degwidth", "degw", "dw"   : width of the image, in degrees (default)
               "arcminwidth", "amw", "aw" : width of the image, in arcminutes
               "arcsecperpix", "app": arcseconds per pixel
               "focalmm": 35-mm (width-based) equivalent focal length
  -8 / --parity <pos/neg>: only check for matches with positive/negative parity
          (default: try both)
  -c / --code-tolerance <distance>: matching distance for quads (default: 0.01)
  -E / --pixel-error <pixels>: for verification, size of pixel positional error
          (default: 1)
  -q / --quad-size-min <fraction>: minimum size of quads to try, as a fraction
          of the smaller image dimension, default: 0.1
  -Q / --quad-size-max <fraction>: maximum size of quads to try, as a fraction
          of the image hypotenuse, default 1.0
  --odds-to-tune-up <odds>: odds ratio at which to try tuning up a match that
          isn't good enough to solve (default: 1e6)
  --odds-to-solve <odds>: odds ratio at which to consider a field solved
          (default: 1e9)
  --odds-to-reject <odds>: odds ratio at which to reject a hypothesis (default:
          1e-100)
  --odds-to-stop-looking <odds>: odds ratio at which to stop adding stars when
          evaluating a hypothesis (default: HUGE_VAL)
  --use-sextractor: use SExtractor rather than built-in image2xy to find sources
  --sextractor-config <filename>: use the given SExtractor config file.  Note
          that CATALOG_NAME and CATALOG_TYPE values will be over-ridden by
          command-line values.  This option implies --use-sextractor.
  --sextractor-path <filename>: use the given path to the SExtractor executable.
          Default: just 'sex', assumed to be in your PATH.  Note that you can
          give command-line args here too (but put them in quotes), eg:
          --sextractor-path 'sex -DETECT_TYPE CCD'.  This option implies
          --use-sextractor.
  -3 / --ra <degrees or hh:mm:ss>: only search in indexes within 'radius' of the
          field center given by 'ra' and 'dec'
  -4 / --dec <degrees or [+-]dd:mm:ss>: only search in indexes within 'radius'
          of the field center given by 'ra' and 'dec'
  -5 / --radius <degrees>: only search in indexes within 'radius' of the field
          center given by ('ra', 'dec')
  -d / --depth <number or range>: number of field objects to look at, or range
          of numbers; 1 is the brightest star, so "-d 10" or "-d 1-10" mean look
          at the top ten brightest stars only.
  --objs <int>: cut the source list to have this many items (after sorting, if
          applicable).
  -l / --cpulimit <seconds>: give up solving after the specified number of
          seconds of CPU time
  -r / --resort: sort the star brightnesses by background-subtracted flux; the
          default is to sort using acompromise between background-subtracted and
          non-background-subtracted flux
  -6 / --extension <int>: FITS extension to read image from.
  --invert: invert the image (for black-on-white images)
  -z / --downsample <int>: downsample the image by factor <int> before running
          source extraction
  --no-background-subtraction: don't try to estimate a smoothly-varying sky
          background during source extraction.
  --sigma <float>: set the noise level in the image
  --nsigma <float>: number of sigma for a source detection; default 8
  -9 / --no-remove-lines: don't remove horizontal and vertical overdensities of
          sources.
  --uniformize <int>: select sources uniformly using roughly this many boxes
          (0=disable; default 10)
  --no-verify-uniformize: don't uniformize the field stars during verification
  --no-verify-dedup: don't deduplicate the field stars during verification
  -C / --cancel <filename>: filename whose creation signals the process to stop
  -S / --solved <filename>: output file to mark that the solver succeeded
  -I / --solved-in <filename>: input filename for solved file
  -M / --match <filename>: output filename for match file
  -R / --rdls <filename>: output filename for RDLS file
  --sort-rdls <column>: sort the RDLS file by this column; default is ascending;
          use "-column" to sort "column" in descending order instead.
  --tag <column>: grab tag-along column from index into RDLS file
  --tag-all: grab all tag-along columns from index into RDLS file
  -j / --scamp-ref <filename>: output filename for SCAMP reference catalog
  -B / --corr <filename>: output filename for correspondences
  -W / --wcs <filename>: output filename for WCS file
  -P / --pnm <filename>: save the PNM file as <filename>
  -k / --keep-xylist <filename>: save the (unaugmented) xylist to <filename>
  -A / --dont-augment: quit after writing the unaugmented xylist
  -V / --verify <filename>: try to verify an existing WCS file
  --verify-ext <extension>: HDU from which to read WCS to verify; set this
          BEFORE --verify
  -y / --no-verify: ignore existing WCS headers in FITS input images
  -g / --guess-scale: try to guess the image scale from the FITS headers
  --crpix-center: set the WCS reference point to the image center
  --crpix-x <pix>: set the WCS reference point to the given position
  --crpix-y <pix>: set the WCS reference point to the given position
  -T / --no-tweak: don't fine-tune WCS by computing a SIP polynomial
  -t / --tweak-order <int>: polynomial order of SIP WCS corrections
  -m / --temp-dir <dir>: where to put temp files, default /tmp
The following options are valid for xylist inputs only:
  -F / --fields <number or range>: the FITS extension(s) to solve, inclusive
  -w / --width <pixels>: specify the field width
  -e / --height <pixels>: specify the field height
  -X / --x-column <column-name>: the FITS column containing the X coordinate of
          the sources
  -Y / --y-column <column-name>: the FITS column containing the Y coordinate of
          the sources
  -s / --sort-column <column-name>: the FITS column that should be used to sort
          the sources
  -a / --sort-ascending: sort in ascending order (smallest first); default is
          descending order

Note that most output files can be disabled by setting the filename to "none".
 (If you have a sick sense of humour and you really want to name your output
  file "none", you can use "./none" instead.)
'''


def convertToHMS(value):
    value = value.split('.')
    value = value[0].split(' ')
    value = f'{value[0]}:{value[1]}:{value[2]}'
    return value


def convertToDMS(value):
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

    :param fitsPath:
    :return:
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

    :param fitsPath: path to the fits file, where the wcs header should be put
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
