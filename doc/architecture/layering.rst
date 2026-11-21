Layering rules
===============
The package layers are checked automatically (``uv run lint-imports``, part of the CI
lint job)::

    gui  ->  logic  ->  mountcontrol  ->  base

A layer may import only from the layers to its right. ``mw4.mainApp`` and ``mw4.loader`` are
top-level modules that wire the layers together. ``mw4.base.deviceRegistry`` is the composition
root that instantiates device drivers and the mount, so it is an explicit exception to the
``base`` layer's dependency direction.

Inside ``logic``:

- ``controllers`` (GUI independent logic, one package per GUI area) and ``drivers`` (device
  back-ends) do not import each other, and the controller areas do not import each other.
- ``fits``, ``profiles``, ``file`` and ``databaseProcessing`` are foundations: they import
  neither drivers nor controllers.
- ``fits``, ``profiles``, ``databaseProcessing`` and ``controllers`` do not use Qt, with two
  documented exceptions (``QObject`` workers with signals in ``photometry`` and
  ``modelRun``).

``QtWidgets``, ``QtGui`` and ``QtCharts`` may only be imported in ``mw4.gui`` and the
application entry points (checked by ruff rule ``TID251``). ``QtCore`` (``QObject``,
``Signal``, ``QThreadPool``) and ``QtNetwork`` are accepted in all layers.
