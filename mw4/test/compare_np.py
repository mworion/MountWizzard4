import skyfield.api



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


def
