# beginning like in the example of the documentation
import skyfield.api

ts = skyfield.api.load.timescale()
planets = skyfield.api.load('de421.bsp')
fileName = './hip_main.dat.gz'

with skyfield.api.load.open(fileName) as f:
    df = skyfield.data.hipparcos.load_dataframe(f)

# filter out dim stars
df = df[df['magnitude'] <= 1.0]
starsDF = skyfield.api.Star.from_dataframe(df)

earth = planets['earth']
location = skyfield.api.Topos(latitude_degrees=50,
                              longitude_degrees=11,
                              elevation_m=500)
observer = earth + location
t = ts.now()

# this calculation works
ra, dec, dist = observer.at(t).observe(starsDF).radec()
print(ra, dec, dist)

# this calculation throws the named error
alt, az, dist = observer.at(t).observe(starsDF).apparent().altaz()
print(alt, au, dist)
