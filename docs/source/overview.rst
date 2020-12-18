Overview
========

Welcome to MountWizzard4! MW4 is a utility for 10micron users for improving the workflow for
astronomy work and imaging runs on Windows10, Mac OSX (beginning from 10.12) and Linux
(Ubuntu from 16.04.).
As a python application, it should run in all environments which support python 3.7, 3.8 or
3.9 including Qt as a Gui framework. Please notice that python 3.9 and older python version
prior to 3.7 and python 2 is not supported.

There are some video about modeling: https://youtu.be/8YWLLo3siUY

and Polar alignment as well: https://youtu.be/Hc49N12fjVo

Some more video's are linked from the documentation.

For full operation MW4 needs actually running INDI / INDIGO Server(s), connected to your
devices. In addition an online connection is used for some services which are helpful, but
not necessary. MW4 supports ASCOM Alpaca for all devices, but the framework has some
issues. MW4 also support ASCOM devices (camera, dome) in Windows environment.

.. list-table:: Supported devices and frameworks in MW4
    :widths: 20, 20, 20, 20, 20
    :header-rows: 1

    *   - Device
        - ASCOM
        - ALPACA
        - INDI
        - INDIGO
    *   - Camera
        - yes
        - yes
        - yes
        - yes
    *   - Filter
        - yes
        - yes
        - yes
        - yes
    *   - Dome
        - yes
        - yes
        - yes
        - not tested
    *   - Telescope
        - yes
        - yes
        - yes
        - yes
    *   - Focuser
        - yes
        - yes
        - yes
        - not tested
    *   - Skymeter
        - yes
        - yes
        - yes
        - Yes
    *   - Environ Sensor
        - yes
        - yes
        - yes
        - no
    *   - Pegasus UPB
        - no
        - no
        - yes
        - yes
    *   - Cover
        - yes
        - yes
        - yes
        - not tested

It is recommended to use mount firmware 2.16 or later as some of the functions don't work
with older firmware versions.

Here is an overview of the functionality available in MW4:

- Many settings and features of the mount can be shown and changed.
- Control movement of the mount as well as tracking speeds.
- Coordinates in J2000 as well as in JNow.
- Virtual keypad
- Model building with different model setups and model generating capabilities. Sorting points
  for effective slew paths or dome situations.
- Model building is done in parallel threads (imaging, plate solving, slewing) to reduce time.
- Show the actual model and alignment error. Give hints on how to improve the raw polar alignment.
- Model optimisation: deleting points, automatic removing point for target RMS etc.
- Manage models stored in the mount (save, load, delete).
- Dome geometry integration (MW4 knows about target flip side and slews dome correctly as
  well as any geometrical constraints).
- Environment data: MW4 shows data from OpenWeatherMap, ClearOutside, External Sensors like
  MBox, Stickstation, UniHedronSQR as well as direct linked sensors like MGBox.
- Refraction handling external / internal from the above sources.
- Satellite: searching, displaying, programming, updating tracking.
- Tools: FITS Header renaming, Park positions, etc.
- Remote shutdown of MW4 and Mount via IP commands.
- Measurements and CSV saving for most environment and mount data
- Imaging: control of connected camera / cooler / filter.
- WOL (wake on LAN) boot for mount. MW4 catches MAC address automatically on first manual start.
- Audio signals for different events (end slew, finished modeling, alert, etc.)
- Updater for all MW4 functions.
- Generate / load / save as many profiles as you would like.
- Show alignment stars. Choose and automatically center for polar or orthogonal adjustments.
- Imaging: expose one or N images, auto solve or auto stack these images.
- Imaging: show distortion grid, astrometric calculations (flux, roundness, sharpness)
