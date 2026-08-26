Changelog
---------

Beta versions
=============

Version 4.x
^^^^^^^^^^^
4.0.0b28

- this is a major release !
  please try out in a separate work folder for test!
  for 2024 Hardware, please use the 3.2.5 or later firmware!
  MW4 will normally support only the latest 3 python versions.

- add: support for python 3.12 and 3.14, remove 3.7 - 3.11
- add: native support for Macs with Apple silicon
- add: windows automatic generation of Desktop link file for MW4 including dpi / scale parameters
- add: macOS automatic generation of .app bundle for MW4 including dpi / scale parameters
- add: linux automatic generation of .desktop file for MW4 including dpi / scale parameters
- add: show free disk space of work dir in the status bar
- add: comets / asteroids uploads now without 10micron installer
- add: support uploading mechanism for databases for macos and linux
- add: support for comet and asteroid data in extended downloads
- add: age parameter for MPC SAT databases before auto download
- add: split Satellite window into satellite world map and satellite horizon view
- add: support for extended json files for satellite data (new format)
- add: support for boltwood file reading
- add: support for compressed / uncompressed xisf files for image display (simple versions)
- add: support for compressed fits files for image display (gzip, bzip2)
- add: support for NINA alpaca devices, please install Alpaca plugin for NINA and enable in settings.
- add: new way of defining build point along celestial paths
- add: all settings are now available in separate windows -> easier to find and better overview
- add: GUI settings support transparency of windows if needed in all color modes
- add: new transparent mode for windows -> alpha value could be set 0..1
- add: volume setting for sound effects in settings, enable / disable sound effects in settings
- add: support for new 2024 HW - disabling WOL if not supported
- add: support for new 2024 HW - enabling auto power on setting if supported
- add: support for status of GPS module with PPS capability (no PPS functionality)
- improve: faster calculation of satellite track using internal calculations
- improve: faster handling of satellite sorting and filtering
- improve: reworked filter set with clear behavior auf selections
- improve: faster and more reliable uploading mechanism for databases
- improve: celestrak interface url's and retrieval strategy
- improve: optimized poll settings
- improve: refraction update only when needed
- improve: reduced cpu memory size of app
- improve: faster startup time
- improve: faster database loading
- improve: better visibility of editable fields
- improve: better status information
- improve: optimizing material look & feel for simulator
- improve: don't delete message list when color change
- improve: rewrite of the online documentation
- improve: no 10micron installer needed anymore for object data
- improve: schedule and threads in waiting times (slow machines)
- improve: change from complicated json dump to YAML format for config file
- improve: more detailed earth map in satellite view
- improve: optimized GUI (imaging settings together ect.)
- improve: environment devices (now 4 generic ones), online and boltwood are generic
- change: moving PyQt5 to major PySide6
- change: moving libraries to latest versions
- change: plate solving features more reliable
- change: database handling for MPC files
- change: move INDI support to indipyclient library
- change: move ASCOM / ALPACA support to official Alpyca library
- change: move installer to separate repo (InstallerMW4) - for v4 not needed anymore, but still available for v3.x
- remove: old windows automation as it is not needed anymore
- remove: embedded documentation and replace with online link
- remove: automation of 10micron installer, replaced with web interface
- remove: updater for MW4 (use uv installer instead)
- remove: automatic profile conversion from x.x to 4.x (too complex)
- remove: blending profiles as it did not work so far.
- remove: native support for NINA (replaced by ALPACA Pluging on NINA)
- fix: typos
