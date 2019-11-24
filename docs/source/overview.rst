Overview
========

Welcome to MountWizzard4! MW4 is a utility for 10micron users for improving the workflow for
astronomy work and runs on Windows, OSx and Linux (Ubuntu tested). As it is a python
application, it should run on all environments, which support python3.7 environment including
Qt as Gui framework.

For full operation MW4 needs a running INDI Server(s), where the devices are connected. In
addition a online connection is for some services helpful, but not needed.

To give you an overview about the functionality:

- Many settings / features of the mount could be show and changed.
- Control of movements of the mount as well as tracking speeds.
- Coordinates in J2000 as well as in JNow.
- Model building with different model setups and model generating capabilities. Sorting points
  for effective slew path or dome situation.
- Model building is done in parallel threads (imaging, plate solving, slewing) to reduce time.
- Monitoring model building (estimated time to finish etc.)
- Show actual model and alignment error. Give hints how to improve polar raw alignment.
- Model optimisation: deleting point, automatic removing point for target RMS etc.
- Model errors in polar plot.
- Manage models stored in the mount (save, load, delete).
- Dome geometry integration (MW4 knows about target flip side and slews dome correctly as
  well as geometrical constraints).
- Environment data: MW4 shows data from OpenWeatherMap, ClearOutside, External Sensors like
  MBox, Stickstation, UniHedronSQR as well as direct linked sensors like MGBox.
- Refraction handling external / interal from the above sources
- Satellite: searching, displaying, programming, updating tracking.
- Tools: Renaming fits files according different header entries.
- Tools: 10 free park positions to be programmed.
- Remote shutdown of MW4 and Mount via IP commands.
- Measurement of most environment and mount data. Displaying them over time and different
  diagrams.
- Measurement: saving data to csv file.
- INDI framework: setting up different INDI server connections and devices.
- Imaging: control of connected camera / cooler / filter.
- Imaging: all parameters about FL and visual KPI's for quality check.
- WOL boot for mount. MW4 catches MAC address automatically on first manual start.
- WOL boot for an additional computer (imaging, etc)
- Audio signals for different events (end slew, finished modeling, alert, etc.)
- Managing online connections.
- Updater for all MW4 functions.
- Generate / load / save as many profiles as you would like to.
- Generate / load / save horizon file.
- Show alignment stars. Choose and automatically center for polar or orthogonal adjustments.
- Imaging: expose one / N images, auto solve or auto stack these images.
- Imaging: show distortion grid, zoom, strech, color images, showing FITS headers.