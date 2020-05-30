Changelog
=========
The changelog contains the user related function or environment updates. For a detailed
changes list, please refer to the commit list on GitHub.

0.150.23

- added checkbox for disabling dual axis tracking while model build
- adding feature to do cyclic backups of mount model when new model build
- added coloring and more data for model analyse
- adding Dome LAT geometry for dome slewing
- reversing the order files are shown (newest first)
- changed model names: prefix to postfix to prioritize date / time
- protection again exposure overrun when
- revised dome slewing detection algorithm for ascom / alpaca polling
- image window gui update. MW4 could show detected sources in image

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
