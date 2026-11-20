# Profile Switch Mount Reconnection Plan

## Goal

When a profile is switched, retire the active mount connection, apply the new
profile's mount host and port, reset connection-specific state, and let the
normal mount startup path reconnect and reload information from that mount.

## Current behavior

- `MainWindow.switchProfile` stops the timer and configurable devices, waits for
  the application thread pool, applies the new config, then restarts devices
  and the timer.
- The mount is not configurable in `DeviceRegistry`, so `stopDevices` does not
  stop mount communication. Mount communication is driven by timers.
- Mount TCP workers are cached globally by `(host, port)`. A profile switch
  does not close the old worker; the new endpoint is used when the mount next
  creates a `Connection`.
- Applying `SettingDeviceMount` updates the mount config, but the prior
  `mountIsUp` state can remain true. In that case the mount startup handler
  does not run its first-connect initialization (firmware, location, model,
  names, and TLE refresh).

## Proposed changes

1. **Add an explicit mount-link lifecycle**
   - Add a mount-specific operation to stop active mount communication before
     profile configuration is replaced.
   - Retire and remove every cached mount-link worker from the worker
     registry, ensuring each socket is closed and each thread has stopped
     before the switch continues. This also cleans workers left behind by
     earlier switches to other endpoints.
   - Ensure in-flight mount jobs cannot reconnect or submit work to the old
     worker during teardown. Keep worker cleanup synchronized with the
     existing thread-pool wait and handle a wait timeout without silently
     claiming a clean shutdown.
   - Keep endpoint-based worker reuse unchanged during normal operation; do
     not stop workers for unrelated endpoints.

2. **Reset mount connection state and apply the new profile**
   - In the profile-switch sequence, stop timers and device activity, stop the
     mount link, then apply the new config.
   - Confirm that `SettingDeviceMount.10micron.hostAddress` and `port` are
     loaded into the live mount configuration before communication restarts.
   - Reset mount-up and poll/startup state so the normal health check treats
     the configured endpoint as a fresh connection. Clear or refresh
     connection-specific cached values so the previous mount is not presented
     as the newly selected mount.
   - Restart the timer only after config and reset state are ready. Preserve the
     existing mount detection and command handshake path.

3. **Reload host information on successful reconnect**
   - Ensure the transition from disconnected to connected invokes the existing
     startup path for the newly selected endpoint.
   - Verify firmware/capabilities and mount location are re-read, and the
     existing model, name, and TLE refreshes are requested for the new mount.
   - Retain existing failure behavior when the configured host is unavailable;
     do not report the old mount as connected.

4. **Add regression tests**
   - Profile-switch tests verify shutdown/configure/reset/start ordering and the
     loaded host and port.
   - Mount-link worker tests verify the old endpoint's worker is stopped,
     removed, and its socket closed, while the new endpoint obtains a fresh
     worker and sends the normal `:U2#` initialization once.
   - Mount startup tests verify a switch from an already-connected mount
     re-enters initialization and reloads the information listed above.
   - Failure and timeout tests verify unavailable hosts and incomplete worker
     shutdown remain observable and do not masquerade as a successful switch.

## Likely files

- `../src/mw4/gui/mainWindow/mainWindow.py`
- `../src/mw4/deviceRegistry.py`
- `../src/mw4/mountcontrol/mount.py`
- `../src/mw4/mountcontrol/mountLink.py`
- `../src/mw4/mountcontrol/connection.py` (only if lifecycle access needs a
  shared helper)
- `../src/mw4/mountcontrol/mountTimeConn.py` (only if reconnect-state reset
  belongs with mount health checking)
- `../tests/unit_tests/gui/mainWindow/test_mainWindow.py`
- `../tests/unit_tests/test_deviceRegistry.py`
- `../tests/unit_tests/mountcontrol/test_mountLink.py`
- Relevant `mountTimeConn` and `mount` unit tests

## Validation

- Run the focused profile-switch, registry, mount-link, mount-health, and mount
  startup unit tests.
- Run Ruff and import-layer checks for changed modules.
- Run the package test suite with coverage after focused tests pass, targeting
  the repository's required 100% coverage.
