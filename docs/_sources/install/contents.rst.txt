Install Process
===============

If you on the way of installing MW4 to your windows system, please be aware of the
32bit / 64bit limitations of ASCOM / drivers and python. If you are using 64bit
drivers (most likely with the new large scale CMOS cameras), you need to install
64bit python as well as windows does not mix both variants flawless.

.. warning:: I strongly recommend not using whitespace in filenames or directory
             paths. Especially in windows handling them is not straight forward
             and I hardly could do all the tests needed to ensure it's
             functionality.

An example setup
----------------

To give a realistic example I will explain my own setup. I build a portable
silver box, which is the housing for the DC / DC converters, the power supply,
the ethernet switch, the mount computer and all the switches and connectors
needed for attaching the silver box to the mount.

All other components are located directly on the telescope, so the is only an
ethernet connection and two 12 V power supply wires to the telescope.

.. image:: image/setup.png
    :align: center

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

