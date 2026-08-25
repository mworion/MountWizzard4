import requests
import time
from alpaca.camera import Camera

camera = Camera("127.0.0.1:32330", 0, "http")
print(camera.Connected)
if not camera.Connected:
    camera.Connected = True
print(camera.Connected)

i = 0
while not i > 50:
    time.sleep(0.2)
    i += 1
    print(camera.Connected)
