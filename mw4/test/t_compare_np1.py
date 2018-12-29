import os
import time
import numpy as np
import astropy._erfa as erfa
import skyfield.api


def loadStars(path):
    fileName = path + '/hip_main.dat.gz'
    with skyfield.api.load.open(fileName) as f:
        df = skyfield.data.hipparcos.load_dataframe(f)

    if len(df) > 0:
        df = df[df['magnitude'] <= 3.5]
        print(len(df))
        starsDict = list()
        for index, row in df.iterrows():
            starsDict.append({row.name: skyfield.api.Star.from_dataframe(row)})

        starsDF = skyfield.api.Star.from_dataframe(df)

    return starsDF, starsDict


if __name__ == "__main__":

    mwGlob = {'workDir': '.',
              'configDir': './mw4/test/config/',
              'dataDir': './mw4/test/config/',
              'build': 'test',
              }
    load = skyfield.api.Loader(mwGlob['dataDir'],
                               expire=True,
                               verbose=None,
                               )
    ts = load.timescale()
    planets = load('de421.bsp')
    starsDF, starsDict = loadStars(mwGlob['dataDir'])
    earth = planets['earth']
    location = skyfield.api.Topos(latitude_degrees=50,
                                  longitude_degrees=11,
                                  elevation_m=500)
    observer = earth + location
    t = ts.now()

    # standard version plus
    timeStart = time.time()
    alt = list()
    az = list()
    obs = observer.at(t)
    for value in starsDict:
        name, coord = list(value.items())[0]
        altE, azE, d = obs.observe(coord).apparent().altaz()
        alt.append(altE.degrees)
        az.append(azE.degrees)
    az_SKY = az
    alt_SKY = alt
    print('standard opt: ', time.time() - timeStart)

    # mas / year to radians / year
    # mas * 3600000 = degrees / year
    # mas * 3600000 / 360 * 2 * np.pi
    # mas/year  * 20000 * np.pi is radians / year
    # version with astropy and erfa and vector
    ra = starsDF.ra.radians
    dec = starsDF.dec.radians
    PR = starsDF.ra_mas_per_year / 3600000 * 2 * np.pi / 360
    PD = starsDF.dec_mas_per_year / 3600000 * 2 * np.pi / 360
    PX = starsDF.parallax_mas / 1000
    RV = starsDF.radial_km_per_s

    # J2000             = 2451544.5
    # HIP = J1991,25    = 2448347.5

    print('preparation')
    ra2, dec2, pr2, pd2, px2, rv2 = erfa.pmsafe(ra, dec, PR, PD, PX, RV,
                                                2448347.5, 0.0, 2452544.5, 0.0)
    timeStart = time.time()
    print('calculation')
    aob, zob, hob, dob, rob, eo = erfa.atco13(ra2,
                                              dec2,
                                              pr2,
                                              pd2,
                                              px2,
                                              rv2,
                                              t.ut1,
                                              0.0,
                                              t.dut1,
                                              location.longitude.radians,
                                              location.latitude.radians,
                                              location.elevation.m,
                                              0.0,
                                              0.0,
                                              0.0,
                                              0.0,
                                              0.0,
                                              0.0)
    az_ERFA = aob * 360 / 2 / np.pi
    alt_ERFA = 90.0 - zob * 360 / 2 / np.pi
    print('astropy scalar: ', time.time() - timeStart)
    print(np.max(abs(alt_ERFA - alt_SKY)), np.max(abs(az_ERFA - az_SKY)))
