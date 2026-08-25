import requests
import time
from alpaca.camera import Camera

camera = Camera("127.0.0.1:32330", 0, "http")
print(camera.Connected)
if not camera.Connected:
    camera.Connected = True
print(camera.Connected)

camera.StartExposure(Duration=1.0, Light=True)
while not camera.ImageReady:
    time.sleep(0.1)

image=camera.ImageArrayRaw
print(camera.ImageArrayInfo)

# Directly inspect the Alpaca endpoint output
url = "http://127.0.0.1:32330/api/v1/camera/0/imagearray?ClientID=1&ClientTransactionID=1"
response = requests.get(url)

print("Status Code:", response.status_code)
print("Headers:", response.headers.get("Content-Type"))
print("Raw Response Text (First 200 chars):", response.text[:200])
