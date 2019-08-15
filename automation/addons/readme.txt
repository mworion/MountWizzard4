To all alpha testers:

First of all, thank you very much that you are willing to give MountWizzard4 a try for
testing. I really appreciate this, because the broad base of equipment to be used in
modeling I can't test myself, nor do I own some of this parts.

For those who are already on MountWizzard3:

Please notice that it is a complete rewrite of the package. So there is no real backwards
compatibility for all file formats. As result, please don't mix working directories as
this might result is problems. Please use a new working directory and start from scratch.

There might be the situation, that things change due to your helpful feedback.

For the testing it might be helpful to enable all parts to debug logging level. This should
be the case of an fresh install, but you could have a look to the settings tab / misc to be
sure to log all issues.

If there were any problems, please report them with log file attached. Otherwise I hardly
could figure out, what happened. The log file is always located in your working directory.
Please always think about the status of the software, it's alpha. So don't destroy your
important data in case !

There were some more functions implemented, I tried to make the tooltips as good as possible,
but there is always room for improvement. Also for typo's unclear naming, please report back.

A good start is to make a new working directory, drop MountWizzard4 App there and start it.
It will create all necessary directories needed. Next would be to check if you have an
internet connection available and set under settings / misc the online mode on. You will see
the status as well in the windows upper right headline. The number there is the number of
running threads (it's for development purpose only).

The internet connection makes updates for deltaT, satellite data, weather data, weather
prognosis available, but you could experience MountWizzard4 offline as well. there is data
available with the app, but it will go invalid soon (satellite) or later (deltaT).

Next good step is to enter the IP of your mount. Once booted, it will check for MAC address
for WOL booting automatically. If it is the first run of MountWizzard4 and your mount is off
you have to manually boot the mount.

What's new so far:
- INDI devices and handling. Please note that for each device type you have to choose the INDI
  server. As you have only one server running, all addresses are the same, but you could get
  the devices from different server if you like.
- Satellite tracking setup and visual
- Integrated OpenWeatherMap (your have to apply there for an API key and enter it)
- Clear Outside weather forecast
- support for Pegasus Ultra Power Box
- online measurement and visualizing of data
- hopefully a more improved gui
- changing JNow / J2000 coordinates, adding DMS and decimal style
- Changing a lot of setting of the mount
- tool for renaming your fits files (at least for me to get order)

What's not in so far:
- MountWizzard4 could only handle INDI devices. If you would like to user others, please
  install at this point in time a INDI server, which provides the devices online.


Again, please take care about your setup, it's alpha and I am not responsible if something
serious happens. It's my personal environment I tested it all, but you never know...

But have fun,

Michel