Changelog
=========
The changelog contains the user related function or environment updates. For a detailed
changes list, please refer to the commit list on GitHub.

Unreleased Betas
----------------

(0.200.0)

- 3d Simulator (mount, dome, build points etc)

(0.190.0)

- full integration testing

Released betas
--------------
0.160.0

..note::
    Please be aware that with new device management the setting might be invalid or don't
    work anymore. Ideally you start with an empty configuration.

- refactoring device management
- bugfix polar / flat diagram in manage model
- bugfix dec error view depending on pierside
- refactoring tests
- refactoring analyse window, adding vectors view
- alpaca device discovery for alpaca servers
- tools: mount movement with duration
- improved views for analyse window
- adding cover device ascom and alpaca (from ASCOM 6.5 onwards)
- split PegasusUPB single device into Observing Conditions and Power
- adding goto park after model run option
- adding keep point selection, so to be able to superpose multiple ones
- recognise older models and show context data
- improved analyse windows features
- stability
- adding exclude done build points
- adding automatic retry for model build


0.151.2

- bugfix for newly introduced matplotlib version

0.151.1

- bugfix for QSI Ascom cameras

0.151.0

- bugfix release qt framework osx

0.150.29

- extension icon support
- adding INDIGO Support for UPB, SQM, MGBox and basic drivers

0.150.28

- adding ascom skymeter
- adding ascom sensor

0.150.27

- photometry in image window, showing flux, roundness, sharpness, sources
- subtracting background in images shown in image window

0.150.26

- improved almanac (moon phase etc, runs now in local time also for drawing)
- newer libraries (matplotlib 3.2.2)

0.150.25

- ASCOM driver retries implemented, actual 5 retries
- shutdown ASCOM with more time
- text updates
- adding csv import and convert to local format for model points
- refinement geometry calculations, more message output
- adding version info to analyse
- improving readability of gui (on/off now blue/black)
- added manual ASCOM connect and disconnect drivers
- MW4 could read MW3 horizon and build points files and convert them to local format
- added almanac functions (twilight, lunar nodes)
- revised icons and some gui implementations

0.150.24

- fixes

0.150.23

- added checkbox for disabling dual axis tracking while model build
- adding feature to do cyclic backups of mount model when new model build
- added coloring and more data for model analyse
- adding Dome LAT geometry for dome slewing
- reversing the order files are shown (newest first)
- changed model names: prefix to postfix to prioritize date / time
- protection again exposure overrun when
- revised dome slewing detection algorithm for ascom / alpaca polling
- image window gui update

0.150.22

- update sgp4 library to 2.12

0.150.21

- adding angular ra / dec measurement
- optimizing satellite passes selection
- optimized coloring
- referenced sgp4 lib v 2.11 for finally closing issue with satellite div / zero
- bugfix changing settling time immediately

0.150.20

- added analyse window
- removed workaround for sgp4 lib locale problem
- quick fix for locale setting on ubuntu caused by the workaround

0.150.19

- extended file / directory selection view
- check if selected directories for astrometry / astap are valid
- showing valid app and index selections with colors

0.150.18

- fixes

0.150.17

- fixes
- added path configuration for astrometry and astap
- filter for satellite names not case sensitive
- added in satellite windows horizon view the next 3 passes in colors
- added some data for modeling analyse
- workaround for satellite in windows / german environments

0.150.16

- keeping satellite name filter when changing sources and applying it directly
- added ascom dome
- added ascom filterwheel
- added ascom telescope
- added ascom focuser
- added ascom framework
- removed duplicate starting of drivers
- added ascom camera

0.150.15

- moved measurement setup to device settings
- added storing measurement data in CSV file
- added search filter for satellites in selection list
- dual axis tracking will be switched off during polar alignment and modeling

0.150.14

- updating external libraries to actual state
- added logging features for updater
- added starting model building on actual pierside to avoid flip when starting
- moved astrometry settings to device menu like other devices
- added loading config for indi remote devices if selected
