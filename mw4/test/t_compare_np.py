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
        df = df[df['magnitude'] <= 2.5]
        starsDict = list()
        for index, row in df.iterrows():
            starsDict.append({row.name: skyfield.api.Star.from_dataframe(row)})

        starsDF = skyfield.api.Star.from_dataframe(df)

    return starsDF, starsDict


def topoToAltAz(ha, dec, lat):
    """
    HaDecToAltAz is derived from http://www.stargazing.net/kepler/altaz.html

    :param ha:
    :param dec:
    :param lat:
    :return:
    """

    ha = (ha * 360 / 24 + 360.0) % 360.0
    dec = np.radians(dec)
    ha = np.radians(ha)
    lat = np.radians(lat)
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
    value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
    value = np.clip(value, -1.0, 1.0)
    A = np.arccos(value)
    if np.sin(ha) >= 0.0:
        az = 2 * np.pi - A
    else:
        az = A
    az = np.degrees(az)
    alt = np.degrees(alt)
    return alt, az


def topoToAltAzNew(ha, dec, lat):
    """
    HaDecToAltAz is derived from http://www.stargazing.net/kepler/altaz.html

    :param ha:
    :param dec:
    :param lat:
    :return:
    """

    ha = (ha * 360 / 24 + 360.0) % 360.0
    dec = np.radians(dec)
    ha = np.radians(ha)
    lat = np.radians(lat)
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
    value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
    value = np.clip(value, -1.0, 1.0)
    az = np.arccos(value)
    az = np.degrees(az)
    alt = np.degrees(alt)
    return alt, az


def advanced(ha, dec, lat):
    ha = (ha * 360 / 24 + 360.0) % 360.0
    dec = np.radians(dec)
    ha = np.radians(ha)
    lat = np.radians(lat)
    alt = np.arcsin(np.sin(dec) * np.sin(lat) + np.cos(dec) * np.cos(lat) * np.cos(ha))
    value = (np.sin(dec) - np.sin(alt) * np.sin(lat)) / (np.cos(alt) * np.cos(lat))
    value = np.clip(value, -1.0, 1.0)
    A = np.arccos(value)
    if np.sin(ha) >= 0.0:
        az = 2 * np.pi - A
    else:
        az = A
    az = np.degrees(az)
    alt = np.degrees(alt)
    return alt, az


def classic():
    earth = self.app.planets['earth']
    location = self.app.mount.obsSite.location
    observer = earth + location
    time = self.app.mount.obsSite.ts.now()
    alt = list()
    az = list()
    for star in self.alignStars:
        hipNoE, coord = list(star.items())[0]
        altE, azE, d = observer.at(time).observe(coord).apparent().altaz()
        alt.append(altE.degrees)
        az.append(azE.degrees)
    return alt, az


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

    # standard version
    timeStart = time.time()
    alt = list()
    az = list()
    for value in starsDict:
        name, coord = list(value.items())[0]
        altE, azE, d = observer.at(t).observe(coord).apparent().altaz()
        alt.append(altE.degrees)
        az.append(azE.degrees)
    print('standard: ', time.time() - timeStart)

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
    print('standard opt: ', time.time() - timeStart)
    az_SKY = az
    alt_SKY = alt

    # improved version
    timeStart = time.time()
    astrometric = observer.at(t).observe(starsDF)
    coord = astrometric.radec()
    ra = coord[0].hours
    dec = coord[1].degrees
    alt = list()
    az = list()
    for ra, dec in zip(ra, dec):
        altE, azE = topoToAltAz(ra, dec, 50)
        alt.append(altE)
        az.append(azE)
    print('improved: ', time.time() - timeStart)

    # improved version with scalar topo
    timeStart = time.time()
    astrometric = observer.at(t).observe(starsDF)
    coord = astrometric.radec()
    ra = coord[0].hours
    dec = coord[1].degrees
    altE, azE = topoToAltAzNew(ra, dec, 50)
    print('scalar: ', time.time() - timeStart)

    # version with astropy and erfa
    timeStart = time.time()
    alt = list()
    az = list()
    ra = starsDF.ra.radians
    dec = starsDF.dec.radians
    PR = starsDF.ra_mas_per_year
    PD = starsDF.dec_mas_per_year
    PX = starsDF.parallax_mas
    RV = starsDF.radial_km_per_s
    for ra, dec, pr, pd in zip(ra, dec, PR, PD):
        aob, zob, hob, dob, rob, eo = erfa.atco13(ra,
                                                  dec,
                                                  pr,
                                                  pd,
                                                  PX,
                                                  RV,
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
        azE = aob * 360 / 2 / np.pi
        altE = 90.0 - zob * 360 / 2 /np.pi
        alt.append(altE)
        az.append(azE)
    print('astropy: ', time.time() - timeStart)


    # version with astropy and erfa and vector
    timeStart = time.time()
    ra = starsDF.ra.radians
    dec = starsDF.dec.radians
    PR = starsDF.ra_mas_per_year
    PD = starsDF.dec_mas_per_year
    PX = starsDF.parallax_mas
    RV = starsDF.radial_km_per_s
    aob, zob, hob, dob, rob, eo = erfa.atco13(ra,
                                              dec,
                                              PR,
                                              PD,
                                              PX,
                                              RV,
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

    print(alt_ERFA - alt_SKY, az_ERFA - az_SKY)


    # testing direction
    barnard = skyfield.api.Star(ra_hours=(17, 57, 48.49803),
                                dec_degrees=(4, 41, 36.2072))

    altSky, azSky, d = observer.at(t).observe(barnard).apparent().altaz()
    altSky = altSky.degrees
    azSky = azSky.degrees
    coord = observer.at(t).observe(barnard).radec()
    ra = coord[0].hours
    dec = coord[1].degrees
    altTopo, azTopo = topoToAltAz(ra + 7, dec, 50)

    print(altSky, altTopo, azSky, azTopo)
