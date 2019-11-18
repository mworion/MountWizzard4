.. image:: _static/mw4.png
    :align: right
    :width: 100

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
- Model building with different model setups and model generating capabilities.
- Model building is done in parallel threads (imaging, plate solving, slewing) to reduce time.
- Monitoring model building (estimated time to finish etc.)
- Show actual model and alignment error. Give hints how to improve polar raw alignment.
- Model optimisation: deleting point, automatic removing point for target RMS etc.
- Model errors in polar plot.
- Manage models stored in the mount (save, load, delete)
- Dome geometry integration (MW4 knows about target flip side and slews dome correctly as
  well as geometrical constraints)