Beta versions of MW4
--------------------

- none so far

Released versions of MW4
------------------------
Version 3.0
^^^^^^^^^^^
3.1.1

- fix: connectivity to NINA 3 nightly

3.1.0

Version 3.1 brings aarch64 support for arm back if using the new installer 3.1

- add: support for aarch64 on raspi for python 3.8 - 3.10
- add: support for ASTAP new databases D50, D20, D05
- improve: speedup launch if INDI server not ready
- improve: support for catalina
- fix: download sources IERS
- fix: seeing entries visibility upon startup

3.0.1

- fix: ASCOM cover: brightness status.
- fix: ASCOM cover: setting / reading brightness / max brightness
- fix: almanac: text for "rise" and "set" were mixed
- fix: DNS resolving
- improve: add a hint for optimal binning to keep reasonable image sizes
- improve meteoblue behavior: correct text and undisplayed if disabled
- improve minor planets selection: adding multiple selection by mouse
- improve refraction: when selecting internal sensor, go to automatic

3.0.0

Version 3.0 is a major release! Please update with care!
No ARM7 support / ARM64 only Python 3.8 - 3.9

- add: GUI: all charts could be zoomed and panned
- add: GUI: all tab menu entries could be customized in order and stored /reset
- add: GUI: all open windows could be collected to visual area
- add: GUI: separate window with big buttons are available
- add: GUI: reduced GUI configurable for a simpler user interface
- add: video: support for up to 4 external RTSP streams or local cameras
- add: video: adding authentication to video streams
- add: video: adding support for HTTP and HTTPS streams
- add: almanac: now supports UTC / local time
- add: almanac: support set/rise times moon
- add: environment: integrate meteoblue.com seeing conditions
- add: analyse: charts could show horizon and values for each point
- add: analyse: alt / az charts with iso 2d contour error curves
- add: audio: sound for connection lost and sat start tracking
- add: model points: multiple variants for edit and move points
- add: model points: set dither on celestial paths
- add: model points: generate from actual used mount model
- add: model points: existing model files could be loaded
- add: model points: golden spiral with exact number of points
- add: polar align: adding hint how to use the knobs measures right
- add: plate solve: new watney astrometry solver for all platforms
- add: hemisphere: selection of terrain file
- add: hemisphere: show actual model error in background
- add: hemisphere: edit horizon model much more efficient
- add: hemisphere: show 2d contour error curve from actual model
- add: hemisphere: move point with mouse around
- add: dome: control azimuth move CW / CCW for INDI
- add: satellites: all time values could be UTC or local time now
- add: MPC / IERS: adding alternative server for download
- add: measure: window has max 5 charts now (from 3)
- add: measure: more values (time delta, focus, cooler power, etc.)
- add: image: photometry functions (aberration, roundness, etc.)
- add: image: tilt estimation like ASTAP does as rectangle and triangle
- add: image: add flip H and flip V
- add: image: show RA/DEC coordinates in image if image was solved
- add: image: center mount pointing g to any point in image by mouse double click
- add: image: center mount pointing to image center
- add: image: support for reading XISF files (simple versions)
- add: imaging: separate page for imaging stats now
- add: imaging: stats: calcs for plate solvers (index files etc.)
- add: imaging: stats: calcs for critical focus zones
- add: drivers: polling timing for drivers could be set
- add: drivers: game controller interface for mount and dome
- add: system: support for python 3.10
- add: help: local install of documentation in PDF format
- add: profiles: automatic translation from v2.2.x to 3.x
- improve: GUI: layout for main window optimized and consistent and wording updates
- improve: GUI: complete rework of charting: performance and functions
- improve: GUI: clean up and optimize IERS download messages
- improve: GUI: get more interaction bullet prove for invalid cross use cases
- improve: GUI: moved on / off mount to their settings: avoid undesired shutoff
- improve: GUI: show twilight and moon illumination in main window
- improve: INDI: correcting setting parameters on startup
- improve: model points: optimized DSO path generation (always fit, less params)
- improve: model run: refactoring
- improve: model run: better information about status and result
- improve: hemisphere: improve solved point presentation (white, red)
- improve: plate solve: compatibility checks
- improve: system: all log files will be stored in a separate folder /log
- improve: system: enable usage of python 3.10
- improve: system: use latest PyQt5 version
- improve: system: adjust window sizes to be able to make mosaic layout on desktop
- improve: system: moved to actual jpl kernel de440.bsp for ephemeris calcs
- remove: system: matplotlib package and replace with more performant pyqtgraph
- remove: system: PIL package and replace with more powerful cv2
- remove: system: move from deprecated distutils to packaging
- remove: system: support for python 3.7 as some libraries stopped support
- remove: imageW: stacking in imageW as it was never used
- remove: testing support for OSx Mojave and OSx Catalina (still should work)
- fix: drivers: device selection tab was not properly positioned in device popup

Version 2.2
^^^^^^^^^^^
2.2.9

- fix: internal updater shows only alpha versions instead of betas

2.2.8

- fix: updates for supporting newer ASTAP versions
- fix: model run will cancel if solving fails
- fix: workaround ASTAP FITS outputs which are not readable via astropy
- update ephemeris file

2.2.7

- fix: text labels
- fix: getting min / max values from indi devices
- fix: updates for supporting newer ASTAP versions
- fix: model run will cancel if solving fails

2.2.6

- fix: reduce load in debug trace mode
- fix: model process stalls in some cases in normal mode
- fix: text labels
- fix: getting min / max values from indi devices

2.2.5

- fix: reduce load in debug trace mode
- fix: model process stalls in some cases in normal mode

2.2.4

- fix: remove race condition for large image file causing solve error in ASTAP
- fix: reduce load in debug trace mode

2.2.3

- fix: mount orientation in southern hemisphere

2.2.2

- fix: almanac moon phase drawing error

2.2.1

- update: builtin data for finals200.all
- fix: download iers data: fix file not found feedback

2.2.0

- add: support SGPro camera as device
- add: support N.I.N.A. camera as device
- add: two modes for SGPro and N.I.N.A.: App or MW4 controlled
- add: debayer (4 modes) all platforms (armv7, StellarMate, Astroberry)
- add: filter satellites for twilight visibility settings
- add: setting performance for windows automation (slow / normal / fast)
- add: auto abort imaging when camera device is disconnected
- add: missing cursor in virtual keypad window
- add: support for keyboard usage in virtual keypad window
- add: screenshot as PNG save for actual window with key F5
- add: screenshots as PNG save for all open windows with key F6
- add: query DSO objects for DSO path setting in build model
- improved: flexible satellite handling when mount not connected
- improved: show selected satellite name in satellite windows title
- improved: 3D simulator drawing
- improved: updater now avoids installation into system package
- improved: GUI for imaging tab - disable all invalid interfaces
- improved: redesign analyse window to get more space for further charts
- improved: Tools: move mount: better UI, tooltips, multi steps in alt/az
- improved: gui in image window when displaying different types
- improved: reduced memory consumption if display raw images
- improved: defining park positions with digit and improve gui for buttons
- improved: when pushbutton shows running, invert icons as well
- improve: moon phases in different color schemes
- upgrade: pywin32 library to version 303 (windows)
- upgrade: skyfield library to 1.41
- upgrade: numpy library to 1.21.4
- upgrade: matplotlib to 3.5.1
- upgrade: scipy library to 1.7.3
- upgrade requests library to 2.27.2
- upgrade importlib_metadata library to 4.10.0
- upgrade deepdiff library to 5.7.0
- upgrade wakeonlan library to 2.1.0
- upgrade pybase64 library to 1.2.1
- upgrade websocket-client library to 1.2.3
- fix: simulator in southern hemisphere


Version 2.1
^^^^^^^^^^^
2.1.7

- add: 12 build point option for model generation
- add: grouping updater windows upper left corner
- add: support for languages other than english in automation
- add: minimize cmd window once MW4 is started
- fix: KMTronic Relay messages

2.1.6
- add: explicit logging of automation windows strings for debug
- add: showing now detected updater path and app
- revert: fixes for german as they do not work

2.1.5

- fix: checking windows python version for automation

2.1.4

- add: enabled internal updater for astroberry and stellarmate
- add: temperature measurement for camera
- improved: logging for ASCOM threading
- improved: image handling
- fix: DSLR camera devices

2.1.3

- add: config adjustments for astroberry and stellarmate devices (no debayer)
- improved: logging for UI events

2.1.2

- fix: non connected mount influences camera on ASCOM / ALPACA
- fix: logging string formatting

2.1.1

- fix: for arm64 only: corrected import for virtual keypad
- fix: arrow keys on keypad did accept long mouse press

2.1.0

- add: hemisphere window: help for choosing the right star for polar alignment
- add: hemisphere terrain adjust for altitude of image beside azimuth
- add: angular error ra / dec axis in measurement
- add: device connection similar for ASCOM and ALPACA devices
- add: extended satellite search and filter capabilities (spreadsheet style)
- add: estimation of satellite apparent magnitude
- add: extended satellite tracking and tuning capabilities
- add: enabling loading a custom satellite TLE data file
- add: command window for manual mount commands
- add: sorting for minimal dome slew in build point selection
- add: setting prediction time of almanac (shorter reduces cpu load)
- add: providing 3 different color schemes
- add: virtual keypad available for RPi 3/4 users now
- improve: check if satellite data is valid (avoid error messages)
- improve: better hints when using 10micron updater
- improve: simplified signals generation
- improve: analyse window plots
- improve: rewrite alpaca / ascom interface
- improve: gui for running functions
- improve: test coverage
- remove: push time from mount to computer: in reliable and unstable
- fix: segfault in qt5lib on ubuntu

Version 2.0
^^^^^^^^^^^
2.0.6

- fixes

2.0.5

- fix: bug when running "stop exposure" in ASCOM

2.0.4

- improvement: GUI for earth rotation data update, now downloads
- improvement: performance for threads.
- improvement: added FITS header entries for ALPACA and ASCOM
- fix: removed stopping DAT when starting model

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
