Before starting
===============
First let us have a look to the basic architecture: MW4 is an application
installed on a computer which is connected to the mount computer via an IP
connection. Ideally it is a wired connection. As the 10micron mounts also support
a serial line, MW4 does not. The mount computer drives the mount without any help
from outside, so if you don't request something from it, there is hardly any
communication.

.. image:: overview.drawio.svg
    :align: center

The basic idea is that MW4 will try to generate "digital twin" for the mount. All
parameter changes for the mount will be sent to it and changes of it's state are
polled to make status visible in MW4.

Overview
--------
As a python application, it should run in all environments which support python
3.7, 3.8 or 3.9 including Qt as a Gui framework. Please notice that older python
version prior to 3.7 and python 2 are not supported.

Many video's are linked in the youtube channel:

https://www.youtube.com/channel/UCJD-5qdLEcBTCugltqw1hXA

For full operation MW4 needs actually running INDI / INDIGO Server(s), connected
to your devices. In addition an online connection is used for some services which
are helpful, but not necessary. MW4 supports ASCOM Alpaca for all devices, but the
framework has some issues. MW4 also support ASCOM devices (camera, dome) in
Windows environment.

.. list-table:: Supported devices and frameworks in MW4
    :widths: 30, 20, 20, 20, 20
    :header-rows: 1

    *   - Device
        - ASCOM
        - ALPACA
        - INDI
        - INDIGO
        - SGPro
        - N.I.N.A.
    *   - Camera
        - yes
        - yes
        - yes
        - yes
        - yes
        - yes
    *   - Filter
        - yes
        - yes
        - yes
        - yes
        - no
        - no
    *   - Dome
        - yes
        - yes
        - yes
        - not tested
        - no
        - no
    *   - Telescope
        - yes
        - yes
        - yes
        - yes
        - no
        - no
    *   - Focuser
        - yes
        - yes
        - yes
        - not tested
        - no
        - no
    *   - Skymeter
        - yes
        - yes
        - yes
        - yes
        - no
        - no
    *   - Environ Sensor
        - yes
        - yes
        - yes
        - no
        - no
        - no
    *   - Pegasus UPB Environ
        - yes
        - yes
        - yes
        - yes
        - no
        - no
    *   - Pegasus UPB Switch
        - yes
        - yes
        - yes
        - yes
        - no
        - no
    *   - Cover
        - yes
        - yes
        - yes
        - not tested
        - no
        - no


It is recommended to use mount firmware 2.16 or later as some of the functions
don't work with older firmware versions.

Here is an overview of the functionality available in MW4:

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
- Model optimisation: deleting points, automatic removing point for target RMS etc.
- Manage models stored in the mount (save, load, delete).
- Dome geometry integration (MW4 knows about target flip side and slews dome
  correctly as well as any geometrical constraints).
- Environment data: MW4 shows data from OpenWeatherMap, ClearOutside, External
  Sensors like MBox, Stickstation, UniHedronSQR as well as direct linked sensors
  like MGBox.
- Refraction handling external / internal from the above sources.
- Satellite: searching, displaying, programming, updating tracking.
- Tools: FITS Header renaming, Park positions, etc.
- Remote shutdown of MW4 and Mount via IP commands.
- Measurements and CSV saving for most environment and mount data
- Imaging: control of connected camera / cooler / filter.
- WOL (wake on LAN) boot for mount. MW4 catches MAC address automatically on
  first manual start.
- Audio signals for different events (end slew, finished modeling, alert, etc.)
- Updater for all MW4 functions.
- Generate / load / save as many profiles as you would like.
- Show alignment stars. Choose and automatically center for polar or orthogonal
  adjustments.
- Imaging: expose one or N images, auto solve or auto stack these images.
- Imaging: show distortion grid, astrometric calculations (flux, roundness,
  sharpness)

Known limitations
-----------------
MW4 does only support python 3.7 - 3.9 right now. The reason for that is the
missing availability of precompiled packages needed.

Some features are limited to windows version only as they need the original
10micronQCI updater program to execute.

Most of the windows environments are based on 32 bit drivers. Therefore it makes
sense to also install python 32 bit for MW4 to run. For drivers it is absolutely
necessary to choose 32/64 bit python according to the drivers as windows does not
allow to mix it. MW4 could handle the 32 bit QCI update program even if you have
installed a 64 bit python version, but execution is very slow.

If you are using the QCI / 10micron updater features on windows, MW4 does automate
the gui interactions. Please do not interrupt this automation.

Installing MW on a raspberry pi will need to compile packages as they ar not
provided from the package manager pypi.org.


Reporting issues
----------------
To have an eye on your setup here are some topics which you could check:

- Mount connection available and stable. Wifi might have performance problems.
  Look for right network settings in mount and local setup.

- Telescope driver connected in EKOS when using INDI setup. MW4 uses the header
  entries and passing them to the plate solver. Therefore EKOS needs a connected
  telescope to be able to put the header entries for RA / DEC into FITS header.

- If using local astrometry.net solver: index files installed and ready.

- If model run does not start: all preconditions (imager, solver, etc. up and
  ready)

- Good counter check is review settings, status bars, message window if something
  is going wrong.

As MW4 adds more functionality, your feedback is highly welcome! To improve
quality and usability any feedback is highly welcome. To maintain a good
transparency and a doable work for my, please respect some recommendations how
to feed back.

.. note:: Please report back under:

          https://github.com/mworion/MountWizzard4/issues.

          This is good for any feedback (bug reports, other issues, usability,
          feature requests, etc). In

          https://github.com/mworion/MountWizzard4/discussions

          there is a good place to start discussions for all other topics of
          interest.

In case of a bug report please have a good description (maybe a screenshot if it‘s
related to GUI) and add the log file(s) to the issue. Normally you just could drop
the log file (or PNG in case of a screen shot) directly to the webpage issue. In
some cases GitHub does not accept the file format (unfortunately for example FITs
files). I this case, please zip them and drop the zipped file. This will work. If
you have multiple files, please don‘t zip them to one file if it‘s not necessary
as I use the issue sheets for the structure itself and by counter checking if have
to maintain a second set of data (unpacked one) which is much work.

If changes are made due to a feedback, new releases will have a link to the closed
issues on GitHub.
