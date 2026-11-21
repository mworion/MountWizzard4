# Simulator rendering and lifecycle fix

## Scope

- Default Qt3D to OpenGL on macOS before creating the application, preserving an explicit
  `QT3D_RENDERER` environment setting and leaving other platforms unchanged.
- Connect dome settings updates once, independently of dome visibility.
- Disconnect external simulator signals before clearing the scene during window closure.
- Document the macOS renderer default and override.

## Validation

- Cover the platform default and explicit override in bootstrap tests.
- Test repeated dome visibility changes without duplicate settings connections.
- Test closed-window signals and reopening with a fresh scene.
- Capture a live simulator frame using the normal environment setup and confirm visible geometry.
- Run Ruff, import-layer checks, type checks, and the full unit suite with 100% coverage.
