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
import subprocess
# external packages
import astropy.io.fits as fits
# local import
from mw4.astrometry import astrometry
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_getWCSHeaderNET():
    val = """SIMPLE  =                    T / Standard FITS file                             
BITPIX  =                    8 / ASCII or bytes array                           
NAXIS   =                    0 / Minimal header                                 
EXTEND  =                    T / There may be FITS ext                          
WCSAXES =                    2 / no comment                                     
CTYPE1  = 'RA---TAN-SIP' / TAN (gnomic) projection + SIP distortions            
CTYPE2  = 'DEC--TAN-SIP' / TAN (gnomic) projection + SIP distortions            
EQUINOX =               2000.0 / Equatorial coordinates definition (yr)         
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
HISTORY Created by the Astrometry.net suite.                                    
HISTORY For more details, see http://astrometry.net.                            
HISTORY Git URL https://github.com/dstndstn/astrometry.net                      
HISTORY Git revision 0.73                                                       
HISTORY Git date Thu_Nov_16_08:30:44_2017_-0500                                 
HISTORY This WCS header was created by the program "blind".                     
DATE    = '2019-08-23T11:08:32' / Date this file was created.                   
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
        wcsHeader = app.astrometry.getWCSHeader(wcsHDU=fitsHandle)
    assert wcsHeader.tostring(sep='\n', endcard=True, padding=False) == val


def test_runImage2xy_1():
    suc = app.astrometry.runImage2xy()
    assert not suc


def test_runImage2xy_2():
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

    class Test:
        returncode = '1'
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        suc = app.astrometry.runImage2xy()
    assert not suc


def test_runSolveField_1():
    suc = app.astrometry.runSolveField()
    assert not suc


def test_runSolveField_2():
    class Test1:
        @staticmethod
        def decode():
            return 'decode'

    class Test:
        returncode = '1'
        stderr = Test1()
        stdout = Test1()

        @staticmethod
        def communicate(timeout=0):
            return Test1(), Test1()

    with mock.patch.object(subprocess,
                           'Popen',
                           return_value=Test()):
        suc = app.astrometry.runSolveField()
    assert not suc


def test_solveNet_1():
    suc = app.astrometry.solveNET()
    assert not suc


def test_solveNet_2():
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=False):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=False):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                          timeout=5,
                                          )
        assert not suc


def test_solveNet_3():
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=False):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/nonsolve.fits',
                                          timeout=5,
                                          )
        assert not suc


def test_solveNet_4():
    home = os.environ.get('HOME')
    app.astrometry.solveApp = {
        'KStars': {
            'programPath': '/Applications/Astrometry.app/Contents/MacOS',
            'indexPath': home + '/Library/Application Support/Astrometry',
            'solve': app.astrometry.solveNET,
            'abort': app.astrometry.abortNET,
        }
    }
    with mock.patch.object(app.astrometry,
                           'runImage2xy',
                           return_value=True):
        with mock.patch.object(app.astrometry,
                               'runSolveField',
                               return_value=True):
            suc = app.astrometry.solveNET(app='KStars',
                                          fitsPath=mwGlob['imageDir'] + '/m51.fits',
                                          timeout=5,
                                          )
        assert suc


def test_abortNet_1():
    app.astrometry.process = None
    suc = app.astrometry.abortNET()
    assert not suc


def test_abortNet_2():
    class Test:
        @staticmethod
        def kill():
            return True
    app.astrometry.process = Test()
    suc = app.astrometry.abortNET()
    assert suc
