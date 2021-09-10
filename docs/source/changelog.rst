Changelog
=========
The changelog contains the user related function or environment updates. For a
detailed changes list, please refer to the commit list on GitHub.

Ideas for the future
--------------------

- implementing Baader dome control e.g. 10micron dome interface
- split profiles in base and add-on
- satellite search with constraints
- receive video indi for sat tracking and horizon setup
- joystick support


Released beta version of MW4
----------------------------
2.1.0 (not released yet)

- add: hints for choosing the right star for polar alignment
- improve: rewrite alpaca / ascom interface

Released version of MW4
-----------------------
Version 2.0
^^^^^^^^^^^
2.0.3

- improvement: GUI for earth rotation data update, now downloads
- improvement: performance for threads.

2.0.2

- fix: robustness against errors in ALPACA server due to memory faults #174
- fix: robustness against filter names / numbers from ALPACA server #174
- fix: cleanup import for pywinauto timings import #175
- improvement: avoid meridian flip #177
- improvement: retry numbers as int #178

2.0.1

- fix: MW4 not shutting down when dome configured, but not connected
- fix mirrored display of points in polar hemisphere view

2.0.0

- add new updater concept
- add mount clock sync feature
- add simulator feature
- add terrain image feature
- add dome following when mount is in satellite tracking mode
- add dome dynamic following feature: reduction of slews for dome
- add setting label support for UPB dew entries
- add auto dew control support for Pegasus UPB
- add switch support for ASCOM/ALPACA Pegasus UPB
- add observation condition support for ASCOM/ALPACA Pegasus UPB
- add feature for RA/DEC FITS writing for INDI server without snooping
- add completely revised satellite tracking menu gui
- add partially satellite tracking before / after possible flip
- add satellite track respect horizon line and meridian limits
- add tracking simulator feature to test without waiting for satellite
- add alt/az pointer to satellite view
- add reverse order for failed build point retry
- add automatic enable webinterface for keypad use
- add broadcast address and port for WOL
- add new IERS and lead second download
- add more functions are available without mount connected
- add change mouse pointer in hemisphere
- add offset and gain setting to imaging
- add disable model point edit during model build run
- update debug standard moved from WARN to INFO
- update underlying libraries
- update GUI improvements
- fix for INDI cameras sending two times busy and exposure=0
- fix slewing message dome when disconnected
- fix retry mechanism for failed build points
- fix using builtins for skyfield and rotation update
- fix plate solve sync function


Version 1.1
^^^^^^^^^^^
1.1.1

- adding fix for INDI cameras sending two times BUSY, EXP=0

1.1.0

- adding release notes showing new capabilities in message window
- adding cover light on / off
- adding cover light intensity settings
- reversing E/W for polar diagram in hemisphere window
- adding push mount time to computer manual / hourly
- adding contour HFD plot to image windows
- adding virtual emergency stop key on time group
- update build-in files if newer ones are shipped
- auto restart MW4 after update
- adding OBJCTRA / OBJCTDEC keywords when reading FITs
- upgrade various libraries

Version 1.0
^^^^^^^^^^^
1.0.7

- bugfix cooler

1.0.6

- checking if camera has cooler
- fixing retry model points

1.0.5

- bugfix check for H18 database

1.0.4
- adding check for ASTAP H17, H18, G17, G18 database
- increasing the solve limit from 9999 arcsec to 36000 arcsec

1.0.3
- bugfix binning setting on large sensors

1.0.2
- bugfix: polar alignment command error

1.0.1
- bugfix: fields index and app in device popup for astrometry and astap were wrong

1.0.0

- first official release
