# MountWizzard4 <img src="docu/pics/mw4.png" width='64' height='64'/>
Version release: 0.81
## Application for use in 10micron Mount environment
Supports INDI Framework (EKOS or any INDI Server).
Needs 10micron firmware 2.16 or newer.

(C) Michael Würtenberger 2019

## Features:
- Runs multi platform (Windows10, Linux Ubuntu 16.04 / 18.04 LTS, Mac OSx 10.3 and 10.4 tested)
- Plate Solving Software: astrometry.net (on linux); KStars/EKOS or Cloudmakers Astrometry on MAC)
- Generate model point based on various algorithms (grid, manual, greater celestial circles, track path)
- Show, save, reload, optimize model (even when model was done manually)
- Auto refraction update if weather station is available for pressure and temperature to mount
- A lot of settings of mount visible and changeable (no need for virtual hand controller)
- Define up to 8 mount positions, which could be slew directly (e.g. flat panel, check ccd etc.)
- Getting data from open weather (API key needed, windows) and stickstation
- Supports Unihedron SQM Device
- Supports Pegasus Ultra Power Box
- Supports KMTronic IP Relay
- Hemisphere window for edit/load/save model points, horizon an many other attributes
- Direct slew mount to any az/alt position with mouse click
- Shows and selects alignment star out of handbook with automatic polar alignment
- Make single or continuously Images and solve them.
- Remote control via TCP for shutdown of App and boot / shutdown of mount computer
- Boots mount via ethernet WOL if in the same subnet
- Audio output for end of slewing / modeling / emergency stop

Please check for these features, if you have the right (mostly newest) firmware installed on your mount.

### Finally
The use this software is at your own risk! No responsibility for damages to your mount or other equipment or your
environment. Please take care yourself !

Hope this makes fun and helps for your hobby, CS Michel