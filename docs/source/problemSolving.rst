Known limitations
=================

MW4 does only support python 3.6 - 3.8 right now. The reason for that is the
missing availability of precompiled packages needed.

On Apple MacOSx BigSur you need update to > 0.220.3 at the QT framework has some
issues opening the primary display.

Some features are limited to windows version only as they need the original
10micronQCI updater program to execute.

Most of the windows environments are based on 32 bit drivers. Therefore it makes
sense to also install python 32 bit for MW4 to run. For drivers it is absolutely
necessary to choose 32/64 bit python according to the drivers as windows does not
allow to mix it. MW4 could handle the 32 bit QCI update program even if you have
installed a 64 bit python version, but execution is very slow.

If you are using the QCI updater features on windows, MW4 does automate the gui
interactions. Please do not interrupt this automation.

Installing MW on a raspberry pi will need to compile packages as they ar not
provided from the package manager pypi.org.


Things to check before reporting an issue
=========================================
To have an eye on your setup here are some topics which you could check:

- Mount connection available and stable. Wifi might have performance problems.
Look for right network settings in mount and local setup.

- Telescope driver connected in EKOS when using INDI setup. MW4 uses the header
entries and passing them to the plate solver. Therefore EKOS needs a connected
telescope to be able to put the header entries for RA / DEC into FITS header.

- If using local astrometry.net solver: index files installed and ready.

- If model run does not start: all preconditions (imager, solver, etc. up and ready)

- Good counter check is review settings, status bars, message window if something
is going wrong.


Reporting issues
================

As MW4 adds more functionality, your feedback is highly welcome! To improve
quality and usability any feedback is highly welcome. To maintain a good
transparency and a doable work for my, please respect some recommendations how
to feed back.

Please report back under: https://github.com/mworion/MountWizzard4/issues. 
This is good for any feedback (bug reports, other issues, usability, feature
requests, etc).

In case of a bug report please have a good description (maybe a screenshot if it‘s
related to GUI) and add the log file(s) to the issue. Normally you just could drop
the log file (or PNG in case of a screen shot) directly to the webpage issue. In
some cases GitHub does not accept the file format (unfortunately for example FITs
files). I this case, please zip them and drop the zipped file. This will work. If
you have multiple files, please don‘t zip them to one file if it‘s not necessary
as I use the issue sheets for the structure itself and by counter checking if have
to maintain a second set of data (unpacked one) which is much work.

If changes are made due to a feedback, new releases will have a link to the closed
issues on GitHub.
