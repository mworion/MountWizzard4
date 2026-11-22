# Plan: clear mount displays on disconnect

## Desired behavior

Clear the **displayed mount values** in the Mount tab and its settings when
the mount disconnects. Keep latitude, longitude and elevation visible and
editable. Leave `Setting`, `ObsSite` and `MountTimeConn` data and object
identities unchanged; this is a presentation change, not a model reset.

## Implementation

1. Inventory the mount-derived displays in `tabMount.py` and
   `tabMount_Sett.py`, including values updated by `MountSett.updatePointGUI`,
   `updateSettingGUI` and `showTimeDiff`. Clear the actual widgets rather than
   setting their model values to zero. Reuse `SETTING_TEXT_FIELDS` for its
   widgets and keep any additional widget lists explicit and centralized.
2. Connect a GUI-owned disconnect handler to the existing mount disconnect
   notification. Blank pointing coordinates, pier side and sidereal time;
   setting values, connection type, GPS and web-interface status, flip and
   meridian times; and mount time, clock difference and RTT. Clear the
   corresponding dynamic warning and tracking-mode styles so they do not
   suggest stale status. Do not clear the three location fields, controls,
   button labels or user-selected coordinate mode.
3. Keep the fields blank while disconnected. In particular, guard the
   once-per-second `showTimeDiff` refresh, which currently writes time and RTT
   even when the mount is down. Guard queued pointing and setting updates so a
   late result cannot immediately refill the displays. Account for the current
   disconnect signal being emitted before `mountIsUp` becomes false; do not
   rely on that flag during the disconnect callback itself.
4. On reconnect, leave the displays blank until fresh values arrive through the
   existing updates. Ensure an old in-flight response cannot be mistaken for a
   fresh update after a rapid reconnect; use the connection generation at the
   appropriate result boundary if needed, without resetting all model data or
   blocking the GUI thread. Preserve the existing location refresh behavior.

## Verification

- Add GUI module tests under `../tests/unit_tests/gui/mainWaddon` that populate
  all affected widgets and styles, disconnect, and verify they are cleared
  while location and controls are unchanged.
- Test repeated disconnected timer ticks and late updates, including a rapid
  disconnect/reconnect, and verify fresh connected data displays normally.
  Cover normal connection loss and the existing explicit shutdown path.
- Verify that the underlying three objects and their stored values are not
  reset by the display-clearing handler. No generated widgets should be edited.
- Run the affected module tests first; then Ruff formatting and linting,
  `uv run lint-imports`, and the overall package tests with branch coverage at
  the project's 100% threshold. Run Windows-specific coverage on Windows.
