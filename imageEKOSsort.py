imagePath = '/Users/mw/Desktop/ngc7380/'
destPath = imagePath + 'sort/'


import glob
from astropy.io import fits as fits
from shutil import copyfile

for filename in glob.iglob(imagePath + '**/*.fits', recursive=True):
    fd = fits.open(name=filename)
    print(filename)
    newFilename = destPath + '{0}_{1}_{2}_{3:04d}_BIN_{4:01d}_{5}'\
        .format(fd[0].header['OBJECT'],
                fd[0].header['FRAME'],
                fd[0].header['FILTER'],
                int(fd[0].header['EXPTIME']),
                int(fd[0].header['XBINNING']),
                fd[0].header['DATE-OBS'],
                )
    newFilename = newFilename.replace(':', '_')
    newFilename = newFilename.replace('.', '_')
    newFilename = newFilename.replace('-', '_')
    newFilename += '.fits'
    print(newFilename)
    fd.close()
    copyfile(filename, newFilename)
