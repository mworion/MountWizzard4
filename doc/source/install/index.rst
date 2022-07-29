Installing
==========

If you on the way of installing MW4 to your windows system, please be aware of the
32bit / 64bit limitations of ASCOM / drivers and python. If you are using 64bit
drivers (most likely with the new large scale CMOS cameras), you need to install
64bit python as well as windows does not mix both variants flawless.

.. warning:: I strongly recommend not using whitespace in filenames or directory
             paths. Especially in windows handling them is not straight forward
             and I hardly could do all the tests needed to ensure it's
             functionality.

.. toctree::
    :maxdepth: 1

    python
    mw4
    astroberry
    stellarmate64
    rpi3
    rpi4
    update
    platesolvers
    example