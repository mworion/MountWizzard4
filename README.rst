MountWizzard4
=============

Welcome to MountWizzard4 is a utility for 10micron users for improving the
workflow for astronomy work and imaging runs on Windows, OSx and Linux
(Ubuntu 18.04 and 20.04 tested). As a python application, it should run in all
environments supporting python 3.7-3.9 and PyQt5 as a GUI framework.

Note:
^^^^^
Please check these pages for some hints to your installation:
https://mountwizzard4.readthedocs.io/en/latest/overview.html

Documentation
^^^^^^^^^^^^^
There is an online documentation available for MW4 which could be searched for
entries:

Web based:
https://mountwizzard4.readthedocs.io

PDF format:
https://mountwizzard4.readthedocs.io/_/downloads/en/latest/pdf/

Installing procedures:
https://mountwizzard4.readthedocs.io/en/latest/install/index.html

Changelog:
https://mountwizzard4.readthedocs.io/en/latest/changelog.html

And there are some videos available for explanation in Youtube channel:

https://www.youtube.com/channel/UCJD-5qdLEcBTCugltqw1hXA/

Please feel free to start any discussion:
https://github.com/mworion/MountWizzard4/discussions


Overall:
^^^^^^^^

For being fully operational, MW4 needs either:

INDI server(s) (see: https://indilib.org) where your devices are connected to.

INDIGO server(s) (see: http://www.indigo-astronomy.org) where your devices are
connected to.

ASCOM Alpaca remote server (see: https://ascom-standards.org/Developer/Alpaca.htm)
abstracting your ASCOM devices or devices which speak native ASCOM Alpaca if
you want to connect over IP with your environment.

For the core devices there is native ASCOM support (Windows platform only).
Please be reminded, that ASCOM has 32bit and 64bit driver implementations and
MW4 could also be installed in 32bit or 64 bit python environment. They could be
not be mixed! 32bit python supports only 32bit drivers and vice versa. Normally
this should not be an issue...

In addition an online connection is used for some services which might be
very helpful.

It is recommended to use mount firmware 2.16 (ideally 2.16.11) or later as some
of the functions don't work with older firmware versions. It should not be a
problem using older versions. A HW pre2012 might also have some issues.

Version, build and code coverage status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
|PYPI_VERSION|  |DOCS| |DownLoadsAbs| |DownLoadsMonth|

|PYTEST macOS| |PYTEST Windows| |PYTHON3_PACKAGE|

|CODE_QUALITY_PYTHON| |CODE_QUALITY_ALERTS| |CODECOV|

|CODECOV_CHART|

Feedback and issue reports
^^^^^^^^^^^^^^^^^^^^^^^^^^
Please report your issues: https://github.com/mworion/MountWizzard4/issues.
Please have a good description (maybe a screenshot if it‘s related to GUI) and add
the log file(s) to the issue. Any feedback welcome!

Finally
^^^^^^^
MountWizzard4 is 'always' in development. The use this software is at your own
risk! No responsibility for damages to your mount or other equipment or your
environment, please take care yourself!

Hope this tool makes fun and helps for your hobby,

CS Michel

.. |DOCS| image::
    https://readthedocs.org/projects/mountwizzard4/badge/?version=latest
    :target: https://mountwizzard4.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |PYTEST macOS| image::
    https://github.com/mworion/MountWizzard4/workflows/python3_macOS_unit/badge.svg

.. |PYTEST Windows| image::
    https://github.com/mworion/MountWizzard4/workflows/python3_win_unit/badge.svg

.. |CODECOV| image::
    https://codecov.io/gh/mworion/MountWizzard4/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mworion/MountWizzard4

.. |CODECOV_CHART| image::
    https://codecov.io/gh/mworion/MountWizzard4/branch/master/graphs/icicle.svg
    :target: https://codecov.io/gh/mworion/MountWizzard4
    :width: 80%
    :align: top

.. |CODE_QUALITY_ALERTS| image::
    https://img.shields.io/lgtm/alerts/g/mworion/MountWizzard4.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/mworion/MountWizzard4/latest/files/?sort=name&dir=ASC&mode=heatmap&showExcluded=false

.. |CODE_QUALITY_PYTHON| image::
    https://img.shields.io/lgtm/grade/python/g/mworion/MountWizzard4.svg?logo=lgtm&logoWidth=18
    :target: https://lgtm.com/projects/g/mworion/MountWizzard4/?mode=list

.. |PYTHON3_PACKAGE| image::
    https://github.com/mworion/MountWizzard4/workflows/python3_package/badge.svg

.. |PYPI_VERSION| image::
    https://img.shields.io/pypi/v/mountwizzard4.svg
    :target: https://pypi.python.org/pypi/mountwizzard4
    :alt: MountWizzard4's PyPI Status
    
.. |DownLoadsAbs| image::
    https://pepy.tech/badge/mountwizzard4
    :target: https://pepy.tech/project/mountwizzard4

.. |DownLoadsMonth| image::
    https://pepy.tech/badge/mountwizzard4/month
    :target: https://pepy.tech/project/mountwizzard4

