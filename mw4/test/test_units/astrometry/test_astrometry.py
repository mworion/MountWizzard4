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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import os
import platform
import numpy as np
import subprocess
# external packages
from astropy.io import fits
# local import
from mw4.astrometry import astrometry
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_init_1():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    assert os.path.isfile(app.mwGlob['tempDir'] + '/astrometry.cfg')


def test_checkAvailability_1():
    app.astrometry.solveApp = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.checkAvailability()
    assert suc
    assert app.astrometry.available == {}


def test_checkAvailability_3():
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/KStars.app/Contents/MacOS/astrometry/bin',
            'indexPath': '/usr/share/astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.checkAvailability()
    assert suc
    assert app.astrometry.available == {}


def test_checkAvailability_4():
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': '/Users/mw/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.checkAvailability()
    assert suc
    assert 'KStars' in app.astrometry.available


def test_readFitsData_1():
    file = mwGlob['imageDir'] + '/m51.fits'
    ra, dec, sc, ra1, dec1 = app.astrometry.readFitsData(file)
    assert ra
    assert dec
    assert sc
    assert ra1
    assert dec1


def test_calcAngleScaleFromWCS_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    scaleX = 2
    for angleX in range(-180, 180, 1):
        phi = np.radians(angleX)
        CD11 = scaleX * np.cos(phi)
        CD12 = scaleX * np.sin(phi)
        header.set('CD1_1', CD11)
        header.set('CD1_2', CD12)
        angle, scale, flip = app.astrometry.calcAngleScaleFromWCS(wcsHeader=header)
        assert np.round(scale, 0) == scaleX * 3600
        assert np.round(angle, 3) == np.round(angleX, 3)


def test_calcAngleScaleFromWCS_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    angle, scale, flip = app.astrometry.calcAngleScaleFromWCS(wcsHeader=header)
    assert angle == 0
    assert scale == 0


def test_getSolutionFromWCS_1():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    (ra, dec, angle, scale, error, flipped, path), header \
        = app.astrometry.getSolutionFromWCS(fitsHeader=header,
                                            wcsHeader=header)
    assert ra.hours == 12
    assert dec.degrees == 60
    assert angle == 0
    assert scale == 0
    assert not flipped

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_2():
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    (ra, dec, angle, scale, error, flipped, path), header \
        = app.astrometry.getSolutionFromWCS(fitsHeader=header,
                                            wcsHeader=header,
                                            updateFits=True)
    assert ra.hours == 12
    assert dec.degrees == 60
    assert angle == 0
    assert scale == 0
    assert not flipped

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_3():
    val = """SIMPLE  =                    T / file does conform to FITS standard             
BITPIX  =                   16 / number of bits per data pixel                  
NAXIS   =                    2 / number of data axes                            
NAXIS1  =                 3388 / length of data axis 1                          
NAXIS2  =                 2712 / length of data axis 2                          
EXTEND  =                    T / FITS dataset may contain extensions            
COMMENT   FITS (Flexible Image Transport System) format is defined in 'Astronomy
COMMENT   and Astrophysics', volume 376, page 359; bibcode: 2001A&A...376..359H 
BSCALE  =                    1 / default scaling factor                         
BZERO   =                32768 / offset data range to that of unsigned short    
INSTRUME= 'QSI CCD '           / CCD Name                                       
TELESCOP= 'LX200 10micron'     / Telescope name                                 
OBSERVER= 'Wuertenberger Michael' / Observer name                               
OBJECT  = 'ced214  '           / Object name                                    
EXPTIME =         9.000000E+02 / Total Exposure Time (s)                        
CCD-TEMP=            -2.00E+01 / CCD Temperature (Celsius)                      
PIXSIZE1=         3.690000E+00 / Pixel Size 1 (microns)                         
PIXSIZE2=         3.690000E+00 / Pixel Size 2 (microns)                         
XBINNING=                    1 / Binning factor in width                        
YBINNING=                    1 / Binning factor in height                       
FRAME   = 'Light   '           / Frame Type                                     
FILTER  = 'Ha      '           / Filter                                         
FOCALLEN=             5.80E+02 / Focal Length (mm)                              
MPSAS   =         2.009000E+01 / Sky Quality (mag per arcsec^2)                 
SCALE   =         1.312495E+00 / arcsecs per pixel                              
SITELAT =         4.803333E+01 / Latitude of the imaging site in degrees        
SITELONG=         1.170000E+01 / Longitude of the imaging site in degrees       
AIRMASS =         1.062458E+00 / Airmass                                        
OBJCTRA = ' 0 02 02.66'        / Object J2000 RA in Hours                       
OBJCTDEC= '67 12 00.49'        / Object J2000 DEC in Degrees                    
RA      =         5.110954E-01 / Object J2000 RA in Degrees                     
DEC     =         6.720014E+01 / Object J2000 DEC in Degrees                    
EQUINOX =               2000.0 / Equatorial coordinates definition (yr)         
DATE-OBS= '2018-10-13T21:12:41.560Z' / UTC start date of observation            
COMMENT Generated by INDI                                                       
EPERADU =                0.251 / Electrons per ADU                              
SCALE   =     1.32234282888689 / MountWizzard4                                  
PIXSCALE=     1.32234282888689 / MountWizzard4                                  
ANGLE   =    -90.9387523171099 / MountWizzard4                                  
FLIPPED =                    F / MountWizzard4                                  
WCSAXES =                    2 / no comment                                     
CTYPE1  = 'RA---TAN-SIP' / TAN (gnomic) projection + SIP distortions            
CTYPE2  = 'DEC--TAN-SIP' / TAN (gnomic) projection + SIP distortions            
LONPOLE =                180.0 / no comment                                     
LATPOLE =                  0.0 / no comment                                     
CRVAL1  =       0.498211219224 / RA  of reference point                         
CRVAL2  =        67.1965741567 / DEC of reference point                         
CRPIX1  =               1694.5 / X reference pixel                              
CRPIX2  =               1356.5 / Y reference pixel                              
CUNIT1  = 'deg     ' / X pixel scale units                                      
CUNIT2  = 'deg     ' / Y pixel scale units                                      
CD1_1   =   -6.01797698131E-06 / Transformation matrix                          
CD1_2   =   -0.000367268151139 / no comment                                     
CD2_1   =    0.000366971618342 / no comment                                     
CD2_2   =   -5.81838134126E-06 / no comment                                     
IMAGEW  =                 3388 / Image width,  in pixels.                       
IMAGEH  =                 2712 / Image height, in pixels.                       
A_ORDER =                    2 / Polynomial order, axis 1                       
A_0_0   =                    0 / no comment                                     
A_0_1   =                    0 / no comment                                     
A_0_2   =    1.75569240162E-07 / no comment                                     
A_1_0   =                    0 / no comment                                     
A_1_1   =    9.37327720638E-07 / no comment                                     
A_2_0   =    2.05155975348E-07 / no comment                                     
B_ORDER =                    2 / Polynomial order, axis 2                       
B_0_0   =                    0 / no comment                                     
B_0_1   =                    0 / no comment                                     
B_0_2   =    1.11328170803E-06 / no comment                                     
B_1_0   =                    0 / no comment                                     
B_1_1   =    2.36644531283E-07 / no comment                                     
B_2_0   =    4.21310462254E-07 / no comment                                     
AP_ORDER=                    2 / Inv polynomial order, axis 1                   
AP_0_0  =   -2.43285325527E-06 / no comment                                     
AP_0_1  =    1.62208046894E-06 / no comment                                     
AP_0_2  =   -1.75568849983E-07 / no comment                                     
AP_1_0  =    2.24141844075E-06 / no comment                                     
AP_1_1  =   -9.37328082471E-07 / no comment                                     
AP_2_0  =   -2.05155807419E-07 / no comment                                     
BP_ORDER=                    2 / Inv polynomial order, axis 2                   
BP_0_0  =   -5.09187396217E-06 / no comment                                     
BP_0_1  =    4.84158585084E-06 / no comment                                     
BP_0_2  =   -1.11328176016E-06 / no comment                                     
BP_1_0  =    1.26100992186E-06 / no comment                                     
BP_1_1  =   -2.36645668767E-07 / no comment                                     
BP_2_0  =   -4.21309890273E-07 / no comment                                     
DATE    = '2019-08-23T11:08:32' / Date this file was created.                   
HISTORY Created by the Astrometry.net suite.                                    
HISTORY For more details, see http://astrometry.net.                            
HISTORY Git URL https://github.com/dstndstn/astrometry.net                      
HISTORY Git revision 0.73                                                       
HISTORY Git date Thu_Nov_16_08:30:44_2017_-0500                                 
HISTORY This WCS header was created by the program "blind".                     
COMMENT -- blind solver parameters: --                                          
COMMENT Index(0): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4210.fits                                    
COMMENT Index(1): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4209.fits                                    
COMMENT Index(2): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4208.fits                                    
COMMENT Index(3): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4207-03.fits                                 
COMMENT Index(4): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4207-00.fits                                 
COMMENT Index(5): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4206-03.fits                                 
COMMENT Index(6): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4206-00.fits                                 
COMMENT Index(7): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4205-03.fits                                 
COMMENT Index(8): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4205-00.fits                                 
COMMENT Index(9): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4204-15.fits                                 
COMMENT Index(10): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4204-14.fits                                 
COMMENT Index(11): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4204-03.fits                                 
COMMENT Index(12): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4204-01.fits                                 
COMMENT Index(13): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4203-15.fits                                 
COMMENT Index(14): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4203-14.fits                                 
COMMENT Index(15): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4203-03.fits                                 
COMMENT Index(16): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4203-01.fits                                 
COMMENT Index(17): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4202-15.fits                                 
COMMENT Index(18): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4202-14.fits                                 
COMMENT Index(19): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4202-03.fits                                 
COMMENT Index(20): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4202-01.fits                                 
COMMENT Field name:                                                             
COMMENT   /Users/mw/PycharmProjects/MountWizzard4/temp/temp.axy                 
COMMENT Field scale lower: 1.19318 arcsec/pixel                                 
COMMENT Field scale upper: 1.44374 arcsec/pixel                                 
COMMENT X col name: X                                                           
COMMENT Y col name: Y                                                           
COMMENT Start obj: 10                                                           
COMMENT End obj: 20                                                             
COMMENT Solved_in: (null)                                                       
COMMENT Solved_out:                                                             
COMMENT   /Users/mw/PycharmProjects/MountWizzard4/temp/temp.solved              
COMMENT Solvedserver: (null)                                                    
COMMENT Parity: 2                                                               
COMMENT Codetol: 0.01                                                           
COMMENT Verify pixels: 1 pix                                                    
COMMENT Maxquads: 0                                                             
COMMENT Maxmatches: 0                                                           
COMMENT Cpu limit: 30.000000 s                                                  
COMMENT Time limit: 0 s                                                         
COMMENT Total time limit: 0 s                                                   
COMMENT Total CPU limit: 30.000000 s                                            
COMMENT Tweak: yes                                                              
COMMENT Tweak AB order: 2                                                       
COMMENT Tweak ABP order: 2                                                      
COMMENT --                                                                      
COMMENT -- properties of the matching quad: --                                  
COMMENT index id: 4207                                                          
COMMENT index healpix: 0                                                        
COMMENT index hpnside: 1                                                        
COMMENT log odds: 290.361                                                       
COMMENT odds: 1.26487e+126                                                      
COMMENT quadno: 36137                                                           
COMMENT stars: 183534,183540,183536,183537                                      
COMMENT field: 5,12,8,6                                                         
COMMENT code error: 0.00258985                                                  
COMMENT nmatch: 63                                                              
COMMENT nconflict: 2                                                            
COMMENT nfield: 2566                                                            
COMMENT nindex: 63                                                              
COMMENT scale: 1.3218 arcsec/pix                                                
COMMENT parity: 1                                                               
COMMENT quads tried: 8                                                          
COMMENT quads matched: 1                                                        
COMMENT quads verified: 0                                                       
COMMENT objs tried: 13                                                          
COMMENT cpu time: 0.001174                                                      
COMMENT --                                                                      
END                                                                             """

    file = mwGlob['tempDir'] + '/net.wcs'
    with fits.open(file) as fitsHandle:
        wcsHeader = app.astrometry.getWCSHeaderNET(wcsHDU=fitsHandle)
    file = mwGlob['imageDir'] + '/test.fits'
    with fits.open(file) as fitsHandle:
        fitsHeader = fitsHandle[0].header

    solve, fitsHeaderNew = app.astrometry.getSolutionFromWCS(fitsHeader=fitsHeader,
                                                             wcsHeader=wcsHeader,
                                                             updateFits=True)
    assert fitsHeaderNew.tostring(sep='\n', endcard=True, padding=False) == val


def test_getSolutionFromWCS_4():
    val = """SIMPLE  =                    T / file does conform to FITS standard             
BITPIX  =                   16 / number of bits per data pixel                  
NAXIS   =                    2 / number of data axes                            
NAXIS1  =                 3388 / length of data axis 1                          
NAXIS2  =                 2712 / length of data axis 2                          
EXTEND  =                    T / FITS dataset may contain extensions            
COMMENT   FITS (Flexible Image Transport System) format is defined in 'Astronomy
COMMENT   and Astrophysics', volume 376, page 359; bibcode: 2001A&A...376..359H 
BSCALE  =                    1 / default scaling factor                         
BZERO   =                32768 / offset data range to that of unsigned short    
INSTRUME= 'QSI CCD '           / CCD Name                                       
TELESCOP= 'LX200 10micron'     / Telescope name                                 
OBSERVER= 'Wuertenberger Michael' / Observer name                               
OBJECT  = 'ced214  '           / Object name                                    
EXPTIME =         9.000000E+02 / Total Exposure Time (s)                        
CCD-TEMP=            -2.00E+01 / CCD Temperature (Celsius)                      
PIXSIZE1=         3.690000E+00 / Pixel Size 1 (microns)                         
PIXSIZE2=         3.690000E+00 / Pixel Size 2 (microns)                         
XBINNING=                    1 / Binning factor in width                        
YBINNING=                    1 / Binning factor in height                       
FRAME   = 'Light   '           / Frame Type                                     
FILTER  = 'Ha      '           / Filter                                         
FOCALLEN=             5.80E+02 / Focal Length (mm)                              
MPSAS   =         2.009000E+01 / Sky Quality (mag per arcsec^2)                 
SCALE   =         1.312495E+00 / arcsecs per pixel                              
SITELAT =         4.803333E+01 / Latitude of the imaging site in degrees        
SITELONG=         1.170000E+01 / Longitude of the imaging site in degrees       
AIRMASS =         1.062458E+00 / Airmass                                        
OBJCTRA = ' 0 02 02.66'        / Object J2000 RA in Hours                       
OBJCTDEC= '67 12 00.49'        / Object J2000 DEC in Degrees                    
RA      =         5.110954E-01 / Object J2000 RA in Degrees                     
DEC     =         6.720014E+01 / Object J2000 DEC in Degrees                    
EQUINOX =               2000.0 / Equatorial coordinates definition (yr)         
DATE-OBS= '2018-10-13T21:12:41.560Z' / UTC start date of observation            
COMMENT Generated by INDI                                                       
EPERADU =                0.251 / Electrons per ADU                              
SCALE   =     1.32234282888689 / MountWizzard4                                  
PIXSCALE=     1.32234282888689 / MountWizzard4                                  
ANGLE   =    -90.9387523171099 / MountWizzard4                                  
FLIPPED =                    F / MountWizzard4                                  
WCSAXES =                    2 / no comment                                     
CTYPE1  = 'RA---TAN'           / TAN (gnomic) projection                        
CTYPE2  = 'DEC---TAN'          / TAN (gnomic) projection                        
LONPOLE =                180.0 / no comment                                     
LATPOLE =                  0.0 / no comment                                     
CRVAL1  =       0.498211219224 / RA  of reference point                         
CRVAL2  =        67.1965741567 / DEC of reference point                         
CRPIX1  =               1694.5 / X reference pixel                              
CRPIX2  =               1356.5 / Y reference pixel                              
CUNIT1  = 'deg     ' / X pixel scale units                                      
CUNIT2  = 'deg     ' / Y pixel scale units                                      
CD1_1   =   -6.01797698131E-06 / Transformation matrix                          
CD1_2   =   -0.000367268151139 / no comment                                     
CD2_1   =    0.000366971618342 / no comment                                     
CD2_2   =   -5.81838134126E-06 / no comment                                     
IMAGEW  =                 3388 / Image width,  in pixels.                       
IMAGEH  =                 2712 / Image height, in pixels.                       
DATE    = '2019-08-23T11:08:32' / Date this file was created.                   
HISTORY Created by the Astrometry.net suite.                                    
HISTORY For more details, see http://astrometry.net.                            
HISTORY Git URL https://github.com/dstndstn/astrometry.net                      
HISTORY Git revision 0.73                                                       
HISTORY Git date Thu_Nov_16_08:30:44_2017_-0500                                 
HISTORY This WCS header was created by the program "blind".                     
COMMENT -- blind solver parameters: --                                          
COMMENT Index(0): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4210.fits                                    
COMMENT Index(1): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4209.fits                                    
COMMENT Index(2): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4208.fits                                    
COMMENT Index(3): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4207-03.fits                                 
COMMENT Index(4): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4207-00.fits                                 
COMMENT Index(5): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4206-03.fits                                 
COMMENT Index(6): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4206-00.fits                                 
COMMENT Index(7): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4205-03.fits                                 
COMMENT Index(8): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4205-00.fits                                 
COMMENT Index(9): /Users/mw/Library/Application                                 
COMMENT   Support/Astrometry/index-4204-15.fits                                 
COMMENT Index(10): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4204-14.fits                                 
COMMENT Index(11): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4204-03.fits                                 
COMMENT Index(12): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4204-01.fits                                 
COMMENT Index(13): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4203-15.fits                                 
COMMENT Index(14): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4203-14.fits                                 
COMMENT Index(15): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4203-03.fits                                 
COMMENT Index(16): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4203-01.fits                                 
COMMENT Index(17): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4202-15.fits                                 
COMMENT Index(18): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4202-14.fits                                 
COMMENT Index(19): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4202-03.fits                                 
COMMENT Index(20): /Users/mw/Library/Application                                
COMMENT   Support/Astrometry/index-4202-01.fits                                 
COMMENT Field name:                                                             
COMMENT   /Users/mw/PycharmProjects/MountWizzard4/temp/temp.axy                 
COMMENT Field scale lower: 1.19318 arcsec/pixel                                 
COMMENT Field scale upper: 1.44374 arcsec/pixel                                 
COMMENT X col name: X                                                           
COMMENT Y col name: Y                                                           
COMMENT Start obj: 10                                                           
COMMENT End obj: 20                                                             
COMMENT Solved_in: (null)                                                       
COMMENT Solved_out:                                                             
COMMENT   /Users/mw/PycharmProjects/MountWizzard4/temp/temp.solved              
COMMENT Solvedserver: (null)                                                    
COMMENT Parity: 2                                                               
COMMENT Codetol: 0.01                                                           
COMMENT Verify pixels: 1 pix                                                    
COMMENT Maxquads: 0                                                             
COMMENT Maxmatches: 0                                                           
COMMENT Cpu limit: 30.000000 s                                                  
COMMENT Time limit: 0 s                                                         
COMMENT Total time limit: 0 s                                                   
COMMENT Total CPU limit: 30.000000 s                                            
COMMENT Tweak: yes                                                              
COMMENT Tweak AB order: 2                                                       
COMMENT Tweak ABP order: 2                                                      
COMMENT --                                                                      
COMMENT -- properties of the matching quad: --                                  
COMMENT index id: 4207                                                          
COMMENT index healpix: 0                                                        
COMMENT index hpnside: 1                                                        
COMMENT log odds: 290.361                                                       
COMMENT odds: 1.26487e+126                                                      
COMMENT quadno: 36137                                                           
COMMENT stars: 183534,183540,183536,183537                                      
COMMENT field: 5,12,8,6                                                         
COMMENT code error: 0.00258985                                                  
COMMENT nmatch: 63                                                              
COMMENT nconflict: 2                                                            
COMMENT nfield: 2566                                                            
COMMENT nindex: 63                                                              
COMMENT scale: 1.3218 arcsec/pix                                                
COMMENT parity: 1                                                               
COMMENT quads tried: 8                                                          
COMMENT quads matched: 1                                                        
COMMENT quads verified: 0                                                       
COMMENT objs tried: 13                                                          
COMMENT cpu time: 0.001174                                                      
COMMENT --                                                                      
END                                                                             """

    file = mwGlob['tempDir'] + '/net.wcs'
    with fits.open(file) as fitsHandle:
        wcsHeader = app.astrometry.getWCSHeaderNET(wcsHDU=fitsHandle)
    file = mwGlob['imageDir'] + '/test.fits'
    with fits.open(file) as fitsHandle:
        fitsHeader = fitsHandle[0].header

    wcsHeader['CTYPE1'] = ('RA---TAN', 'TAN (gnomic) projection ')
    wcsHeader['CTYPE2'] = ('DEC---TAN', 'TAN (gnomic) projection ')

    solve, fitsHeaderNew = app.astrometry.getSolutionFromWCS(fitsHeader=fitsHeader,
                                                             wcsHeader=wcsHeader,
                                                             updateFits=True)
    # print(fitsHeaderNew.tostring(sep='\n', endcard=True, padding=False))
    assert fitsHeaderNew.tostring(sep='\n', endcard=True, padding=False) == val


def test_abort_1():
    suc = app.astrometry.abort()
    assert not suc


def test_solveClear():
    app.astrometry.mutexSolve.lock()
    app.astrometry.solveClear()


def test_solveThreading_1():
    suc = app.astrometry.solveThreading()
    assert not suc


def test_solveThreading_2():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.solveThreading(app='KStars')
    assert not suc


def test_solveThreading_3():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    file = mwGlob['imageDir'] + '/m51.fits'
    suc = app.astrometry.solveThreading(app='KStars',
                                        fitsPath=file,
                                        )
    assert suc


def test_solveThreading_4():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    file = mwGlob['imageDir'] + '/m51.fits'
    suc = app.astrometry.solveThreading(app='KStars',
                                        fitsPath=file,
                                        )
    assert not suc


def test_solveThreading_5():
    app.astrometry.solveApp = {
        'CloudMakers': {
            'programPath': '',
            'indexPath': '',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    file = mwGlob['imageDir'] + '/m51.fits'
    suc = app.astrometry.solveThreading(app='KStars',
                                        fitsPath=file,
                                        )
    assert not suc


def test_abort_1():
    suc = app.astrometry.abort()
    assert not suc


def test_abort_2():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    suc = app.astrometry.abort(app='KStars')
    assert suc
