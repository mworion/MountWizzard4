# Plan: mountcontrol review recommendations 1-5

Source: `gists/work_agent/2026-10-16-mountcontrol-review.md`, section 5.

## Step 1 - fix the three high-severity bugs (with regression tests)
- `convert.convertRaToAngle`: validate the float branch in degrees
  (0 <= value < 360) instead of hours.
- `MountTimeConn.shutdown`: do not set `mountIsUp` directly; let the
  `mountIsUp` signal drive `MountDevice.startupMountData`, so
  `deviceDisconnected` is emitted.
- `ObsSiteCommands.startSlewing` / `MountDevice.resultCyclePointing`: reset the
  stale `flipped` state once it has been used for the settle time.

## Step 2 - geometry / location order and dome config keys
- Verify the order of `getFW` / `getLocation`.
- Recompute the derived geometry values when the location arrives.
- Use defaults for missing dome config keys.

## Step 3 - validation in parsers
- `Setting.parseSetting`: validate length and field formats.
- `Model.parseStars`: validate the number of fields per star.

## Step 4 - `Connection.communicateRaw`
- Return early when sending fails.

## Step 5 - typing
- Remove the `Any` annotations listed in section 3.1 of the review.
- Run Pyrefly on the package.

## Finish
- Ruff format and check, tests for `tests/unit_tests/mountcontrol` with 100 %
  coverage, then the whole test suite.

