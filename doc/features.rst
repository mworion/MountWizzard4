Features
========

For being fully operational, MountWizzard4 needs either:

-   INDI server(s) (see: https://indilib.org) where your devices are connected
    to.

-   INDIGO server(s) (see: http://www.indigo-astronomy.org) where your devices
    are connected to.

-   ASCOM Alpaca remote server (see: https://ascom-standards.org/FAQs/Index.htm)
    abstracting your ASCOM devices or devices which speak native ASCOM Alpaca if
    you want to connect over IP with your environment.

-   Running versions of Sequence Generator Pro or N.I.N.A. as frontend for camera
    device.

-   For the core devices there is native ASCOM support (Windows platform only).
    Please be reminded, that ASCOM has 32bit and 64bit driver implementations
    and MountWizzard4 could also be installed in 32bit or 64 bit python
    environment. They must be not be mixed! 32bit python supports only 32bit
    drivers and vice versa. Normally this should not be an issue. I strongly 
    recommend to use 64bit python and 64bit ASCOM drivers.

-   In addition an internet connection is used for some services which might be
    very helpful.

It is recommended to use mount firmware 3.x or later as some of the functions
don't work with older firmware versions. It should not be a problem using older
versions. A HW pre2012 might also have some issues. MountWizzard4 supports also
older firmwares from 2.x onwards, but with limited features and untested.

It is recommended to use mount firmware 2.16 or later as some of the functions
don't work with older firmware versions.

Here is an overview of the functionality available in MountWizzard4:

- Many settings and features of the mount can be shown and changed.
- Control movement of the mount as well as tracking speeds.
- Coordinates in J2000 as well as in JNow.
- Virtual keypad
- Model building with different model setups and model generating capabilities.
  Sorting points for effective slew paths or dome situations.
- Model building is done in parallel threads (imaging, plate solving, slewing)
  to reduce time.
- Show the actual model and alignment error. Give hints on how to improve the
  raw polar alignment.
- Model optimisation: deleting points, automatic removing point for target RMS
  etc.
- Manage models stored in the mount (save, load, delete).
- Dome geometry integration (MountWizzard4 knows about target flip side and
  slews dome correctly as well as any geometrical constraints).
- Environment data: MountWizzard4 shows data from OpenWeatherMap, ClearOutside,
  External Sensors like MBox, Stickstation, UniHedronSQR as well as direct
  linked sensors like MGBox.
- Refraction handling external / internal from the above sources.
- Satellite: searching, displaying, programming, updating tracking.
- Tools: FITS Header renaming, Park positions, etc.
- Remote shutdown of MountWizzard4 and Mount via IP commands.
- Measurements and CSV saving for most environment and mount data
- Imaging: control of connected camera / cooler / filter.
- WOL (wake on LAN) boot for mount. MountWizzard4 catches MAC address
  automatically on first manual start.
- Audio signals for different events (end slew, finished modeling, alert, etc.)
- Updater for all MountWizzard4 functions.
- Generate / load / save as many profiles as you would like.
- Show alignment stars. Choose and automatically center for polar or orthogonal
  adjustments.
- Imaging: expose one or N images, auto solve or auto stack these images.
- Imaging: show distortion grid, astrometric calculations (flux, roundness,
  sharpness)
