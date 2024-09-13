

def test_readFitsData_1(function):
    file = 'tests/workDir/image/test1.fit'
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header['RA'] = 8.0
    header['DEC'] = 45.0
    hdu.writeto(file)
    ra, dec, sc = function.readFitsData(file)
    assert ra
    assert dec
    assert sc is None


def test_calcAngleScaleFromWCS_1(function):
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
        angle, scale, flip = function.calcAngleScaleFromWCS(wcsHeader=header)
        assert np.round(scale, 0) == scaleX * 3600
        assert np.round(angle, 3) == np.round(angleX, 3)


def test_calcAngleScaleFromWCS_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    angle, scale, flip = function.calcAngleScaleFromWCS(wcsHeader=header)
    assert angle == 0
    assert scale == 0


def test_getSolutionFromWCS_1(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']


def test_getSolutionFromWCS_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header,
                                                updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_3(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    header.set('CTYPE1', 'TAN')
    header.set('CTYPE2', 'TAN')
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header,
                                                updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_4(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    header.set('CTYPE1', 'TAN-SIP')
    header.set('CTYPE2', 'TAN-SIP')
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header,
                                                updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']
    assert header['DEC'] == header['CRVAL2']


def test_getSolutionFromWCS_5(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set('CRVAL1', 180.0)
    header.set('CRVAL2', 60.0)
    header.set('RA', 180.0)
    header.set('DEC', 60.0)
    header.set('A_', 60.0)
    header.set('B_', 60.0)
    header.set('AP_', 60.0)
    header.set('BP_', 60.0)
    header.set('CTYPE1', 'TAN')
    header.set('CTYPE2', 'TAN')
    solve, header = function.getSolutionFromWCS(fitsHeader=header,
                                                wcsHeader=header,
                                                updateFits=True)
    assert solve['raJ2000S'].hours == 12
    assert solve['decJ2000S'].degrees == 60
    assert solve['angleS'] == 0
    assert solve['scaleS'] == 0
    assert not solve['mirroredS']

    assert header['RA'] == header['CRVAL1']


def test_getWCSHeader_1(function):
    val = function.getWCSHeader()
    assert val is None


def test_getWCSHeader_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    val = function.getWCSHeader(wcsHDU=hdu)
    assert val
