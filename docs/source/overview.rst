Overview
========

Welcome to MountWizzard4! MW4 is a utility for 10micron users for improving the workflow for
astronomy work and imaging runs on Windows10, Mac OSX (beginning from 10.12) and Linux
(Ubuntu from 16.04. tested).
As a python application, it should run in all environments which support python3.7 including
Qt as a Gui framework.

There are some video about modeling: https://youtu.be/8YWLLo3siUY

and Polar alignment as well: https://youtu.be/Hc49N12fjVo

Some more video's are linked from the documentation.

For full operation MW4 needs actually running INDI Server(s), connected to your devices. In
addition an online connection is used for some services which are helpful, but not necessary.
MW4 supports ASCOM Alpaca for all devices, but the framework seems to be still unstable.
MW4 also support the basic ASCOM devices (camera, dome) on Windows environment.

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
- Monitor the model building process (with estimated time to finish etc.)
- Show the actual model and alignment error. Give hints on how to improve the raw polar alignment.
- Model optimisation: deleting points, automatic removing point for target RMS etc.
- Model errors in polar plot.
- Manage models stored in the mount (save, load, delete).
- Dome geometry integration (MW4 knows about target flip side and slews dome correctly as
  well as any geometrical constraints).
- Environment data: MW4 shows data from OpenWeatherMap, ClearOutside, External Sensors like
  MBox, Stickstation, UniHedronSQR as well as direct linked sensors like MGBox.
- Refraction handling external / internal from the above sources.
- Satellite: searching, displaying, programming, updating tracking.
- Tools: Renaming fits files according to different header entries.
- Tools: 10 free programmable park positions.
- Remote shutdown of MW4 and Mount via IP commands.
- Measurements for most environment and mount data. Chart the environment data over time with configurable chart options.
- Saving measurement data to csv file.
- INDI framework: setting up different INDI server connections and devices.
- Imaging: control of connected camera / cooler / filter.
- Imaging: all parameters about FL and visual KPIs for quality check.
- WOL (wake on LAN) boot for mount. MW4 catches MAC address automatically on first manual start.
- WOL boot for an additional computer (imaging, etc)
- Audio signals for different events (end slew, finished modeling, alert, etc.)
- Managing online connections.
- Updater for all MW4 functions.
- Generate / load / save as many profiles as you would like.
- Generate / load / save horizon file.
- Show alignment stars. Choose and automatically center for polar or orthogonal adjustments.
- Imaging: expose one or N images, auto solve or auto stack these images.
- Imaging: show distortion grid, zoom, stretch, color images, showing FITS headers.
