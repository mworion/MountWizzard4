MountWizzard4
=============

Documentation:
--------------
There is a documentation available for MW4:
https://mworion.github.io/MountWizzard4/index.html

Welcome to MountWizzard4 is a utility for 10micron users for improving the
workflow for astronomy work and imaging runs on Windows (10 and 11), OSx (Big Sur
- Ventura), Linux (Ubuntu 18.04 - 22.04) and some Linux ARM64 distributions
(Astroberry and StellarMate - both 64 bit). As a python application, it should
run in all environments supporting python 3.8-3.10 and PyQt5 5.15.9 as a GUI
framework.

For being fully operational, MW4 needs either:

-   INDI server(s) (see: https://indilib.org) where your devices are connected to.

-   INDIGO server(s) (see: http://www.indigo-astronomy.org) where your devices
    are connected to.

-   ASCOM Alpaca remote server (see: https://ascom-standards.org/FAQs/Index.htm)
    abstracting your ASCOM devices or devices which speak native ASCOM Alpaca if
    you want to connect over IP with your environment.

-   Running versions of Sequence Generator Pro or NINA as frontend for camera
    device.

-   For the core devices there is native ASCOM support (Windows platform only).
    Please be reminded, that ASCOM has 32bit and 64bit driver implementations
    and MW4 could also be installed in 32bit or 64 bit python environment. They
    could be not be mixed! 32bit python supports only 32bit drivers and vice versa
    . Normally this should not be an issue...

-   In addition an internet connection is used for some services which might be
    very helpful.

It is recommended to use mount firmware 3.0 or later as some
of the functions don't work with older firmware versions. It should not be a
problem using older versions. A HW pre2012 might also have some issues.

Versions, downloads:
--------------------
|PYPI_VERSION| |PY_VERSIONS| |DownLoadsAbs| |DownLoadsMonth|

Code quality:
-------------
|CODECOV| |OPEN_ISSUES|

Unit tests:
^^^^^^^^^^^
|PYTEST macOS| |PYTEST Windows| |PYTEST Ubuntu|

Test install / run scripts:
^^^^^^^^^^^^^^^^^^^^^^^^^^^
|TEST_SCRIPTS_PYPI| |TEST_SCRIPTS_PACKAGES|

Test coverage:
^^^^^^^^^^^^^^
|CODECOV_CHART|

Commit status:
^^^^^^^^^^^^^^
|COMMITS_WEEK| |COMMITS_MASTER|

PDF document:
https://raw.githubusercontent.com/mworion/MountWizzard4/master/docs/build/latex/mountwizzard4.pdf

Changelog:
https://raw.githubusercontent.com/mworion/MountWizzard4/master/docs/source/changelog.rst

And there are some videos available for explanation in Youtube channel:
https://www.youtube.com/channel/UCJD-5qdLEcBTCugltqw1hXA/

Feedback discussions and issue reports:
---------------------------------------
Please report your issues: https://github.com/mworion/MountWizzard4/issues.
Please have a good description (maybe a screenshot if it‘s related to GUI) and
add the log file(s) to the issue. Any feedback welcome!

Please feel free to start any discussion:
https://github.com/mworion/MountWizzard4/discussions


Finally:
--------
MountWizzard4 is 'always' in development. The use this software is at your own
risk! No responsibility for damages to your mount or other equipment or your
environment, please take care yourself!

Hope this tool makes fun and helps for your hobby,

CS Michel

.. |PY_VERSIONS| image::
    https://img.shields.io/pypi/pyversions/mountwizzard4.svg

.. |PYTEST macOS| image::
    https://github.com/mworion/MountWizzard4/workflows/unit_macOS/badge.svg?branch=master

.. |PYTEST Windows| image::
    https://github.com/mworion/MountWizzard4/workflows/unit_win/badge.svg?branch=master

.. |PYTEST Ubuntu| image::
    https://github.com/mworion/MountWizzard4/workflows/unit_ubuntu/badge.svg?branch=master

.. |CODECOV| image::
    https://codecov.io/gh/mworion/MountWizzard4/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mworion/MountWizzard4

.. |CODECOV_CHART| image::
    https://codecov.io/gh/mworion/MountWizzard4/branch/master/graphs/icicle.svg
    :target: https://codecov.io/gh/mworion/MountWizzard4
    :width: 80%
    :align: top

.. |OPEN_ISSUES| image::
    https://img.shields.io/github/issues-raw/mworion/mountwizzard4
    :target: https://github.com/mworion/MountWizzard4/issues

.. |COMMITS_MASTER| image::
    https://img.shields.io/github/commits-since/mworion/mountwizzard4/3.0.0
    :target: https://github.com/mworion/MountWizzard4/commits/master

.. |COMMITS_WEEK| image::
    https://img.shields.io/github/commit-activity/w/mworion/mountwizzard4

.. |TEST_SCRIPTS_PYPI| image::
    https://github.com/mworion/MountWizzard4/workflows/test_scripts_pypi/badge.svg?branch=master

.. |TEST_SCRIPTS_PACKAGES| image::
    https://github.com/mworion/MountWizzard4/workflows/test_scripts_packages/badge.svg?branch=master

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

