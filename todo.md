missing tests:
- tests imaging window 
- tests loader
- tests + docu message window
- tests for polar plot in mainW 

problems occurred list:
- mountcontrol overflow pointing
- wcs axes in GUI not showing always labels
- improved header handling image window + docu
- mainApp new style of implementation


necessary feature list:
- add dome support from indi
- add dso path calculation in modeldata
- add dso path in mainW
- hemisphere: show best altitude when polar align is on
- link dome to hemisphere
- astrometry online
- astrometry configs
- image widget
- indi CCD camera
- indi telescope / dome separate host
- indi CCD camera separate host
- mountcontrol: adding TLE commands and tests
- optimizing model functions (all) implement

nice to have:
- auto reconnect all indi servers
- indi setting parameters of devices
- gui show indi device FL / pixels data in screen and choose which to use
- check if daylight timezone fits to the computer or set it up !
- max error for modeling solving
- move format string to new python format
- having main screen in layout format as well
