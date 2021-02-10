Changelog
=========
The changelog contains the user related function or environment updates. For a
detailed changes list, please refer to the commit list on GitHub.

Unreleased version of MW4
-------------------------
(1.1)

- 3d Simulator (mount, dome, build points etc)
- retrofit model based on hashed coordinates
- adding switch interface Pegasus UPB for ASCOM / ALPACA
- implementing Baader dome control e.g. 10micron dome interface
- adding ascom Pegasus (might have to split Pegasus into three devices - env,
  switch, focuser)
- optimizing dome for less movements on small changes
  I see quite a few times the dome being moved by only a very small amount. But it
  does affect the observatory, so even this small move needs another 10s settle
  time for the mount So avoiding them would be great.

Released version of MW4
-----------------------
1.0.1
- bugfix: fields index and app in device popup for astrometry and astap were wrong

1.0.0

- first official release

0.240.4

- adding choice of mount port 3490 or 3492
- improving gui for sat tracking and displayed tracking rate

0.240.3

- icons, gui improvements
- checking tracking
- minor bugfixes fpr corner cases

0.240.2

- cleanup
- skyfield 1.36
- remove workaround as 10micron offered a fix in fw 2.16.13
- remove autodew button for pegasus as provided indi driver has bugs


0.240.1

- bugfix

0.240.0

- adding workaround for 2.16.12 firmware when deleting model points
- adding tests, refactoring, cleanup

0.230.0

- adding threading for blocking ASCOM drivers (ScopeDome)
- adding support for dome vert adjustment 10micron vs. ScopeDome and others
- added dome shutter open / close
- improved interactive explanations for dome geometry settings
- improved rounding for higher precision in modeling
- adding Ra / Dec input for slew, make tabs persistent
- improved input handling of angle inputs
- additional logging for windows automation
- support for new QCIUpdater naming from 2.16.12 on
- automatic unit testing for all parts
- skyfield upgrade to 1.35
- pywin32 upgrade to 300
- split pyerfa and astropy
- delete photutils dependency and moving to sep package for non windows install
- adding photometry HFD calculation
- adding IERS download for time data to get newer on as in mw4 distro

0.220.8

- bugfix
- lowering critical dome radius from 1.25 to 1 m
- adding retries for ASCOM connections and extend the time period

0.220.7

- cleanup and fine tuning

0.220.6

- added absolute move for Alt/Az for an improved horizon generating process.

0.220.5

- adding horizon generating by adding (add point to horizon map)

0.220.4

- improved logging
- imported some external packages
- update PyQt5 to 5.15.2
- update to support python 3.9 now
- removed python 3.6 support
- bugfix for long download times
- adding focuser handling
- add moving alt / az direction with direct command (easy making horizon maps)
- adding actual position to horizon map (easy making horizon maps)

0.220.3

- support for MacOSx Bigsur

0.220.2

- added support for windows automation with 64bit python (is slow)
- added support for ASCOM6.5 CoverDevice
- improved upload functionality for comets / asteroids / earth rotation
- earth rotation data does not need downloads

0.220.0

- optimizing question dialogs
- adding upload from satellites databases
- refactoring
- making park / slew positions really park

0.211.0

- refactor gui / utilities
- refactor dome and removed duplicates
- adding additional fields for environment sensor from hub if present
- showing satellite data when opening sat window

0.210.0

- moving to skyfield 1.31 and get rid of some files related to time
- mw4 generates the earth rotation files for 10micron updater
- bugfixes

0.200.0

- adding asteroids programming (windows only)

0.191.1

- correcting dome geometry
- adding safety margin between build points and horizon lines

0.190.3

- changing opencv-python-headless to colour_demosaicing library
- adding support for RaspberryPi4 with Ubuntu Mate 20.04.1LTS
- bugfix slewing in hemisphere without any device

0.190.0

- bringing back polar diagram
- bringing up test coverage

0.180.0

- move weather api to device
- move relay ip to device
- more room for profile name
- cleanup gui

0.170.5

- update skyfield to 1.30
- update astropy 4.0.3
- update mountcontrol 0.176
- bugfixes
- rework logging
- rework hemisphere window

0.170.4

- bugfixes
- correction of tooltips

0.170.3

- adding comets programming (windows only)
- adding update deltaT for mount (windows only)
- adding progressbar for minot planet data download

0.160.2

- performance hemisphere
- updated hemisphere behavior

0.160.0

..note::
    Please be aware that with new device management the setting might be invalid
    or don't work anymore. Ideally you start with an empty configuration. For
    experts: you could delete the part "driversData" from the config file.

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
- adding feature for selecting point for deletion out of model overview by double
  click
- changed numbers from 0 to number from 1 (human like)
- clear checkmarks after successful model run
- update matplotlib to 3.3.2
- update photutils to 1.0.1
- update importlib_metadata to 2.0.0
- update opencv-python-headless to 4.4.0.44
- adding good / total points to analyse window

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
