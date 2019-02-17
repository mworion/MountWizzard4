import glob
import os
from astropy.io import fits
from shutil import copyfile

imagePath = '/Users/mw/2018_11_25_TLAPOx379/'
destPath = '/Users/mw/2018_11_25_TLAPOx379/sort/'


for filename in glob.glob(imagePath + '**/*.fits', recursive=True):
    with fits.open(name=filename) as fd:
        newFilename = destPath + '{0}{1}_{2}_BIN_{3:01d}_{4}'\
            .format('M15_',
                    fd[0].header['FRAME'],
                    fd[0].header['FILTER'],
                    int(fd[0].header['XBINNING']),
                    fd[0].header['DATE-OBS'],
                    )
        newFilename = newFilename.replace(':', '_')
        newFilename = newFilename.replace('.', '_')
        newFilename = newFilename.replace('-', '_')
        newFilename += '.fits'
    print(filename)
    print(newFilename)
    copyfile(filename, newFilename)
