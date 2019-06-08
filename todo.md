missing tests:
- loader 0%
- mountcontrol new commands qt
- indibase new commands qt
- widget 67%
- kmRelay 75%
- remote 52%

problems occurred list:
- mountcontrol overflow pointing
- minimum horizon line not implemented

necessary feature list:
- astrometry configs
- mountcontrol: adding TLE commands and tests
- optimizing model functions (all) implement
- change build data in modeldata to named tuples
- GWOL status adding in mountcontrol and MW4 GUI
- sorting spiral for efficient path
- INDI: CCD needs telescope to be connected to get coordinates
- INDI: set filter from image window
- INDI: set filter from imaging setup
- performance measure window
- tooltips


nice to have:
- tox as framework -> see youtube 
- astrometry online
- hemisphere: show best altitude when polar align is on
- indi setting parameters of devices
- check if daylight timezone fits to the computer or set it up !
- max error for modeling solving
- INDI FlipFlat Device open 
- mark modeled points (really necessary ?)
- adding stacking of images 


architecture:
- replace mixin with subclassing ?
- move format string to new python format
- images in memory instead of FITS files ?
- mainApp refactor to better understandable implementation
- check extended attributes when zipping APP bundle in macOS
- skyfield with new format
- skyfield with adding + - for angles