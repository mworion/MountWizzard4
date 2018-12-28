import os
import skyfield.api
from mw4.build import build


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
    time = ts.now()
    alt = list()
    az = list()
    for value in starsDict:
        name, coord = list(value.items())[0]
        print(name, coord)
        altE, azE, d = observer.at(time).observe(coord).apparent().altaz()
        alt.append(altE.degrees)
        az.append(azE.degrees)



