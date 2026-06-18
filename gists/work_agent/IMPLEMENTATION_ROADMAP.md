# MountWizzard4 – Implementation Roadmap
**Companion to**: IMPROVEMENT_PLAN.md  
**Purpose**: Actionable task breakdown with specific files and code changes

---

## Phase 1: Foundation & Type System

### Task 1.1.1: Add ParamSpec to Worker Class

**File**: `src/mw4/base/tpool.py`

**Changes**:
- Import ParamSpec: `from typing import ParamSpec`
- Add type parameters to Worker class
- Update `__init__` signature
- Document with example usage

**Acceptance Criteria**:
- Mypy validates function signature capture
- Existing tests pass
- Type hints improve IDE autocomplete
- 100% coverage maintained

**Estimated Effort**: 2 hours
**Priority**: P0 (Critical)

---

### Task 1.1.2: Type Protocol for Device Base

**File**: `src/mw4/base/` (new: `device_protocol.py`)

**New Classes**:
```python
class DeviceProtocol(Protocol):
    def startCommunication(self) -> bool: ...
    def stopCommunication(self) -> bool: ...
    def pollData(self) -> None: ...
    def getName(self) -> str: ...
```

**Files to Update**:
- `alpacaClass.py`: Verify implementation matches Protocol
- `ascomClass.py`: Verify implementation matches Protocol
- `indiClass.py`: Verify implementation matches Protocol

**Acceptance Criteria**:
- All device classes pass Protocol validation
- Type hints correct in IDE
- Tests pass
- 100% coverage maintained

**Estimated Effort**: 4 hours
**Priority**: P0

---

### Task 1.1.3: Replace `Any` in Core Modules

**Files to Update** (Priority Order):
1. `src/mw4/base/tpool.py` (3 hours)
2. `src/mw4/base/loggerMW.py` (2 hours)
3. `src/mw4/base/alpacaAscomCommon.py` (4 hours)
4. `src/mw4/base/indiClass.py` (3 hours)
5. `src/mw4/base/ascomClass.py` (3 hours)
6. `src/mw4/base/alpacaClass.py` (3 hours)
7. `src/mw4/base/deviceRegistry.py` (3 hours)
8. `src/mw4/base/deviceEntry.py` (2 hours)
9. `src/mw4/base/driverDataClass.py` (2 hours)
10. Others identified in grep results

**Pattern for Each File**:
```python
# Before:
def process(self, data: Any) -> Any:
    ...

# After:
def process(self, data: DeviceMessage) -> ProcessResult:
    ...
```

**Acceptance Criteria**:
- All `Any` replaced with specific types or Protocol
- Mypy validates types
- Type hints accurate
- Tests pass
- Coverage maintained

**Estimated Effort**: 25 hours total
**Priority**: P0

---

### Task 1.1.4: Queue and Signal Type Hinting

**Files to Update**:
- `src/mw4/base/tpool.py` (queue types)
- `src/mw4/gui/**/*.py` (signal types)
- `src/mw4/logic/**/*.py` (queue messages)

**Pattern**:
```python
# Before:
self.messages: queue.Queue = queue.Queue()

# After:
from typing import TypeAlias
DeviceMessage: TypeAlias = dict[str, Any]  # or specific type
self.messages: queue.Queue[DeviceMessage] = queue.Queue()
```

**Acceptance Criteria**:
- All queue.Queue uses typed
- All Signal emissions typed
- IDE autocomplete works
- Tests pass

**Estimated Effort**: 6 hours
**Priority**: P1

---

### Task 1.2.1: Create Exception Hierarchy

**File**: `src/mw4/base/exceptions.py` (new)

**Contents**:
```python
class MountWizzardException(Exception):
    """Base exception for all MountWizzard4 errors"""
    pass

class DeviceConnectionError(MountWizzardException):
    """Device communication connection failure"""
    pass

class ProtocolCommunicationError(MountWizzardException):
    """Protocol-level communication error"""
    pass

class ConfigurationError(MountWizzardException):
    """Configuration validation or loading error"""
    pass

class FileIOError(MountWizzardException):
    """File I/O operation error"""
    pass

class ThreadPoolError(MountWizzardException):
    """Thread pool or worker error"""
    pass

class ValidationError(MountWizzardException):
    """Data validation error"""
    pass
```

**Acceptance Criteria**:
- Exception hierarchy complete
- Proper inheritance chain
- Documentation present
- Tests for each exception type

**Estimated Effort**: 3 hours
**Priority**: P0

---

### Task 1.2.2: Update Error Handling in Core Modules

**Files to Update** (Priority Order):
1. `src/mw4/base/alpacaAscomCommon.py` - connectDevice() (4 hours)
2. `src/mw4/base/bootstrap.py` - extractDataFiles() (3 hours)
3. `src/mw4/base/indiClass.py` - Device I/O (3 hours)
4. `src/mw4/base/ascomClass.py` - Device I/O (3 hours)
5. `src/mw4/mountcontrol/*.py` - Mount communication (3 hours)

**Pattern**:
```python
# Before:
try:
    result = connect_device()
except Exception as e:
    logging.error(f"Error: {e}")

# After:
try:
    result = connect_device()
except ProtocolCommunicationError as e:
    logging.error(f"Protocol error connecting device: {e}")
    raise DeviceConnectionError(f"Failed to connect: {e}") from e
except ConfigurationError as e:
    logging.error(f"Config issue: {e}")
    raise
```

**Acceptance Criteria**:
- Specific exceptions caught
- Exception chains maintained
- Error context preserved
- Tests pass
- 100% coverage of error paths

**Estimated Effort**: 16 hours
**Priority**: P0

---

### Task 1.2.3: Update Tests for Exception Handling

**New Test File**: `tests/unit_tests/base/test_exceptions.py`

**Coverage**:
- Each exception type raises correctly
- Exception messages include context
- Exception chains maintained
- Logging captures exception properly

**Updated Test Files**:
- `tests/unit_tests/base/test_alpacaAscomCommon.py`
- `tests/unit_tests/base/test_bootstrap.py`
- etc.

**Acceptance Criteria**:
- All tests pass
- 100% exception path coverage
- Error handling patterns validated

**Estimated Effort**: 8 hours
**Priority**: P0

---

## Phase 2: Architecture Refactoring

### Task 2.1.1: Create Base Sub-package Structure

**Create Directories**:
```bash
mkdir -p src/mw4/base/core
mkdir -p src/mw4/base/threading
mkdir -p src/mw4/base/logging
mkdir -p src/mw4/base/protocols
```

**Create Files**:
- `src/mw4/base/core/__init__.py`
- `src/mw4/base/threading/__init__.py`
- `src/mw4/base/logging/__init__.py`
- `src/mw4/base/protocols/__init__.py`

**Acceptance Criteria**:
- All directories created
- All __init__.py files present
- Directory structure validated

**Estimated Effort**: 1 hour
**Priority**: P0

---

### Task 2.1.2: Move Core Module Files

**File Moves**:
1. `deviceRegistry.py` → `core/registry.py`
2. `deviceEntry.py` → `core/entry.py`
3. `driverDataClass.py` → `core/drivers.py`

**For Each File**:
1. Copy to new location
2. Update import paths in moved file
3. Update __init__.py in new package
4. Run tests to verify
5. Delete old file
6. Update all imports throughout codebase

**Update Import Paths** (in all 256 files as needed):
```python
# Before:
from mw4.base.deviceRegistry import DeviceRegistry

# After:
from mw4.base.core.registry import DeviceRegistry
```

**Acceptance Criteria**:
- Files moved to new location
- All imports resolve
- Tests pass
- No circular imports

**Estimated Effort**: 8 hours
**Priority**: P0

---

### Task 2.1.3: Move Threading Module Files

**File Moves**:
1. `tpool.py` → `threading/worker.py`
2. `timerManager.py` → `threading/timers.py`

**Follow same process as Task 2.1.2**

**Acceptance Criteria**:
- Files moved
- Imports updated
- Tests pass
- No circular imports

**Estimated Effort**: 4 hours
**Priority**: P0

---

### Task 2.1.4: Move Logging Module Files

**File Moves**:
1. `loggerMW.py` → `logging/logger.py`

**Follow same process**

**Acceptance Criteria**:
- File moved
- Imports updated
- Tests pass

**Estimated Effort**: 2 hours
**Priority**: P0

---

### Task 2.1.5: Move Protocol Module Files

**File Moves**:
1. `indiClass.py` → `protocols/indi.py`
2. `ascomClass.py` → `protocols/ascom.py`
3. `alpacaClass.py` → `protocols/alpaca.py`
4. `alpacaAscomCommon.py` → `protocols/common.py`
5. `sgproClass.py` → `protocols/sgpro.py`

**Follow same process**

**Acceptance Criteria**:
- Files moved
- Imports updated
- Tests pass
- No circular imports

**Estimated Effort**: 10 hours
**Priority**: P0

---

### Task 2.1.6: Create Public API via __init__.py

**File**: `src/mw4/base/__init__.py`

**Contents**:
```python
from mw4.base.core import DeviceRegistry, DeviceEntry
from mw4.base.threading import Worker, TimerManager
from mw4.base.logging import LoggerMW
from mw4.base.protocols import (
    IndiClass,
    AscomClass,
    AlpacaClass,
    DeviceProtocol,
)
from mw4.base.exceptions import (
    MountWizzardException,
    DeviceConnectionError,
    # ... other exceptions
)

__all__ = [
    'DeviceRegistry',
    'DeviceEntry',
    'Worker',
    'TimerManager',
    'LoggerMW',
    'IndiClass',
    'AscomClass',
    'AlpacaClass',
    'DeviceProtocol',
    # ... exceptions
]
```

**Acceptance Criteria**:
- All public symbols exported
- Imports work from mw4.base
- IDE shows available exports
- Tests pass

**Estimated Effort**: 2 hours
**Priority**: P1

---

### Task 2.2.1: Define Device Protocol ABCs

**File**: `src/mw4/base/protocols/__init__.py`

**New Classes**:
```python
from abc import ABC, abstractmethod

class DeviceBase(ABC):
    """Abstract base for all device types"""
    
    @abstractmethod
    def startCommunication(self) -> bool:
        """Start device communication"""
        pass
    
    @abstractmethod
    def stopCommunication(self) -> bool:
        """Stop device communication"""
        pass
    
    @abstractmethod
    def pollData(self) -> None:
        """Poll device for data"""
        pass
    
    @abstractmethod
    def getName(self) -> str:
        """Get device name"""
        pass

class IndiDeviceProtocol(DeviceBase):
    """INDI protocol specific interface"""
    pass

class AscomDeviceProtocol(DeviceBase):
    """ASCOM protocol specific interface"""
    pass

class AlpacaDeviceProtocol(DeviceBase):
    """Alpaca protocol specific interface"""
    pass
```

**Acceptance Criteria**:
- ABCs defined
- All abstract methods present
- Protocol hierarchy correct
- Documentation complete

**Estimated Effort**: 3 hours
**Priority**: P1

---

### Task 2.2.2: Update Device Classes to Inherit from ABCs

**Files to Update**:
- `src/mw4/base/protocols/indi.py`
- `src/mw4/base/protocols/ascom.py`
- `src/mw4/base/protocols/alpaca.py`

**Pattern**:
```python
# Before:
class IndiClass:
    def startCommunication(self) -> bool:
        ...

# After:
class IndiClass(IndiDeviceProtocol):
    def startCommunication(self) -> bool:
        ...
```

**Acceptance Criteria**:
- All device classes updated
- ABC methods implemented
- Tests pass
- Type checking validates

**Estimated Effort**: 4 hours
**Priority**: P1

---

### Task 2.2.3: Update Device Factory

**File**: `src/mw4/base/core/registry.py`

**Update Device Creation**:
```python
def create_device(self, protocol: str, config: dict) -> DeviceBase:
    """Create device with protocol validation"""
    if protocol == 'INDI':
        device = IndiClass(config)
    elif protocol == 'ASCOM':
        device = AscomClass(config)
    elif protocol == 'Alpaca':
        device = AlpacaClass(config)
    else:
        raise ValueError(f"Unknown protocol: {protocol}")
    
    # Validate protocol implementation
    if not isinstance(device, DeviceBase):
        raise TypeError(f"Device {device} must implement DeviceBase")
    
    return device
```

**Acceptance Criteria**:
- Factory validates protocols
- TypeError raised for invalid devices
- Tests cover all protocols
- 100% coverage

**Estimated Effort**: 2 hours
**Priority**: P1

---

## Phase 3: Code Quality & Pythonic Patterns

### Task 3.1.1: Replace os.path with pathlib

**Files to Update** (High Priority):
1. `src/mw4/base/bootstrap.py` - extractDataFiles()
2. `src/mw4/base/packageConfig.py`
3. `src/mw4/logic/*/config*.py` (all config loaders)

**Pattern**:
```python
# Before:
import os
config_dir = os.path.join(home_dir, ".mw4")
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

# After:
from pathlib import Path
config_dir = Path.home() / ".mw4"
config_dir.mkdir(parents=True, exist_ok=True)
```

**Acceptance Criteria**:
- All os.path replaced with Path
- Path operations use modern methods
- Tests pass
- No file I/O regressions

**Estimated Effort**: 12 hours
**Priority**: P1

---

### Task 3.1.2: Use f-strings Exclusively

**Grep All String Formatting**:
```bash
grep -r "\.format\|%" src/mw4 --include="*.py" | grep -v test | wc -l
```

**Update All Instances**:
```python
# Before:
msg = "Device {} is at {}".format(name, position)
msg = "Device %s is at %s" % (name, position)

# After:
msg = f"Device {name} is at {position}"
```

**Acceptance Criteria**:
- All .format() replaced
- All % formatting replaced
- Tests pass
- Linting passes

**Estimated Effort**: 8 hours
**Priority**: P1

---

### Task 3.1.3: Use Comprehensions and Modern Loops

**Pattern Examples**:
```python
# Before:
result = []
for item in items:
    if item.active:
        result.append(item.process())

# After:
result = [item.process() for item in items if item.active]

# Before:
for i in range(len(items)):
    print(i, items[i])

# After:
for i, item in enumerate(items):
    print(i, item)
```

**Acceptance Criteria**:
- List comprehensions used where appropriate
- enumerate() used for indexed loops
- zip() used for parallel iteration
- Tests pass

**Estimated Effort**: 10 hours
**Priority**: P2

---

### Task 3.1.4: Implement Context Manager for Worker

**File**: `src/mw4/base/threading/worker.py`

**Implementation**:
```python
class Worker(QRunnable):
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        self.cleanup()
        return False
    
    def cleanup(self):
        """Ensure thread cleanup on exception"""
        # Clean up resources
        pass
```

**Usage**:
```python
with Worker(my_function) as worker:
    thread_pool.start(worker)
```

**Acceptance Criteria**:
- Context manager works
- Resources cleaned up
- Tests pass
- No resource leaks

**Estimated Effort**: 2 hours
**Priority**: P2

---

### Task 3.2.1: Profile and Benchmark

**Create**: `src/mw4/base/performance.py`

**Contents**:
```python
import time
from functools import wraps
from typing import Callable, Any

def profile_function(func: Callable) -> Callable:
    """Decorator to profile function execution"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@profile_function
def slow_function():
    time.sleep(0.1)
```

**Identify Hotspots**:
- GUI rendering (PyQtGraph)
- Device polling
- Image processing (OpenCV)
- File I/O (FITS/XISF)

**Acceptance Criteria**:
- Profiling tools in place
- Benchmarks established
- Hotspots identified
- Baseline measurements recorded

**Estimated Effort**: 4 hours
**Priority**: P2

---

### Task 3.2.2: Optimize Image Processing

**Files to Profile**:
- `src/mw4/logic/imageProcessing/*.py`
- Any OpenCV calls

**Optimization Techniques**:
- Use NumPy vectorization
- Preallocate arrays
- Use array views instead of copies
- Profile with cProfile/py-spy

**Expected Improvements**: 10–20% for image operations

**Acceptance Criteria**:
- Performance benchmarks pass
- No visual quality loss
- Tests pass
- Documented optimization decisions

**Estimated Effort**: 8 hours
**Priority**: P3

---

### Task 3.2.3: Optimize GUI Rendering

**Files to Update**:
- `src/mw4/gui/mainWindow/*.py` (PyQtGraph usage)
- GUI update loops

**Techniques**:
- Batch updates with `updatesDisabled()`
- Use `QTimer` for batched signal processing
- Cache computed layouts
- Profile with Qt profiler

**Acceptance Criteria**:
- UI responsiveness improved
- Frame rate > 30 FPS
- Tests pass
- Documented changes

**Estimated Effort**: 6 hours
**Priority**: P3

---

## Phase 4: Documentation & Type Coverage

### Task 4.1.1: Configure Mypy

**Create**: `mypy.ini`

```ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
strict = True

[mypy-mw4.gui.widgets.*]
ignore_errors = True

[mypy-tests.*]
disallow_untyped_defs = False
```

**Acceptance Criteria**:
- Mypy configuration valid
- CI integration ready
- Can be run with: `mypy src/mw4/base`

**Estimated Effort**: 1 hour
**Priority**: P1

---

### Task 4.1.2: Run Mypy on Base Module

**Run**:
```bash
mypy src/mw4/base --config-file mypy.ini
```

**Fix All Errors**:
- Add missing type annotations
- Resolve type mismatches
- Document necessary `type: ignore` comments

**Acceptance Criteria**:
- Mypy passes on src/mw4/base
- All errors resolved
- Type coverage > 95%

**Estimated Effort**: 8 hours
**Priority**: P1

---

### Task 4.1.3: Extend Mypy to Logic and GUI

**Phase in Mypy**:
1. Week 1: src/mw4/base (from Task 4.1.2)
2. Week 2: src/mw4/logic
3. Week 3: src/mw4/gui (excluding auto-generated widgets)
4. Week 4: src/mw4/mountcontrol

**For Each Module**:
1. Run mypy
2. Fix errors
3. Update CI configuration
4. Document progress

**Acceptance Criteria**:
- Mypy passes on all modules
- Type coverage > 90% overall
- CI validates types

**Estimated Effort**: 20 hours
**Priority**: P1

---

### Task 4.2.1: Add Module Docstrings

**Create Documentation Template**:
```python
"""
Module: device_registry

Manages device registration and lifecycle across all protocols
(INDI, ASCOM, Alpaca, SGPRO).

This module provides:
- DeviceRegistry: Central device management
- DeviceEntry: Individual device tracking
- Device lifecycle: Creation, initialization, cleanup

Example:
    registry = DeviceRegistry(app)
    device = registry.createDevice('INDI', config)
    device.startCommunication()

Note:
    Devices are thread-safe and can be accessed from multiple threads.
    Communication happens in dedicated worker threads via threadPool.
"""
```

**Files to Update**:
- All 256 Python files in src/mw4
- Check existing docstrings
- Fill in missing module docstrings

**Acceptance Criteria**:
- All modules have docstrings
- Docstrings follow Google style
- Docstrings reference public API
- Sphinx can generate docs

**Estimated Effort**: 16 hours
**Priority**: P2

---

### Task 4.2.2: Add Class Docstrings

**Template**:
```python
class DeviceRegistry:
    """
    Central registry for managing all connected devices.
    
    This class maintains a registry of all connected devices across
    different protocols (INDI, ASCOM, Alpaca). It handles device
    lifecycle management including creation, initialization, and
    cleanup.
    
    Attributes:
        app: Parent application instance
        threadPool: Worker thread pool for device communication
        devices: Dictionary of registered devices by ID
        
    Signals:
        deviceConnected: Emitted when device connects (signal)
        deviceDisconnected: Emitted when device disconnects
        
    Thread Safety:
        Thread-safe for concurrent access from multiple threads.
    """
```

**Acceptance Criteria**:
- All public classes documented
- Google-style docstrings used
- Attributes documented
- Methods documented
- Thread safety noted

**Estimated Effort**: 12 hours
**Priority**: P2

---

### Task 4.2.3: Document Public APIs

**Create**: `docs/api_reference.md`

**Contents**:
- All public modules
- All public classes
- All public functions
- Usage examples
- Cross-references

**Generate with Sphinx**:
```bash
sphinx-build -b html docs docs/_build
```

**Acceptance Criteria**:
- API documentation complete
- All public symbols documented
- Examples provided
- Sphinx builds without warnings

**Estimated Effort**: 8 hours
**Priority**: P2

---

## Phase 5–8: Testing, Security, CI/CD, Maintenance

[Similar task breakdown for remaining phases...]

---

## Quick Reference: Task Priority Matrix

| Phase | High Priority (P0) | Medium Priority (P1) | Low Priority (P2/P3) |
|-------|------------------|-------------------|-------------------|
| 1 | ParamSpec, Exceptions, Replace Any | Queue typing | Validation |
| 2 | Base reorganization, ABCs | Public API | Factory pattern |
| 3 | pathlib, f-strings | Comprehensions, Context mgr | Performance profiles |
| 4 | Module docstrings, Mypy base | Type coverage full, Class docs | API reference |
| 5 | Test parallelization | Coverage gaps | Stress tests |
| 6 | CVE scanning, Input validation | Audit logging | Fuzzing |
| 7 | Build caching | Test distribution | Release automation |
| 8 | Quality metrics | Developer handbook | Architecture guide |

---

## Dependency Chain

```
Phase 1 (Foundation)
    ↓
Phase 2 (Architecture) ← depends on Phase 1 exceptions
    ↓
Phase 3 (Code Quality) ← partially independent, can overlap
    ↓
Phase 4 (Documentation) ← depends on Phases 1–3
    ↓
Phase 5 (Testing) ← can start after Phase 1
    ↓
Phase 6 (Security) ← independent, can run in parallel
    ↓
Phase 7 (CI/CD) ← depends on Phase 5
    ↓
Phase 8 (Maintenance)
```

---

## Tracking Progress

### Weekly Standup Format

```markdown
### Week X Report

**Completed**:
- [ ] Task 1.1.1: ParamSpec in Worker
- [ ] Task 1.1.2: Device Protocol

**In Progress**:
- [ ] Task 1.1.3: Replace Any in core modules (60%)

**Blocked**:
- Task X.X.X: Reason

**Next Week Plan**:
- Task Y.Y.Y
- Task Z.Z.Z

**Metrics**:
- Test coverage: 100%
- Mypy errors: 250 → 200
- Build time: 5m30s
```

---

## Tool Commands Reference

```bash
# Run Ruff linting
ruff check src/mw4/

# Run Ruff formatting
ruff format src/mw4/

# Run Mypy type checking
mypy src/mw4/base --config-file mypy.ini

# Run tests with coverage
uv run pytest tests/unit_tests/base --cov=src/mw4/base

# Profile function performance
python -m cProfile -s cumtime script.py

# Check for security vulnerabilities
safety check

# Audit dependencies
pip audit

# Generate documentation
sphinx-build -b html docs docs/_build
```

---

**Document Status**: Ready for Implementation  
**Last Updated**: June 18, 2026  
**Questions**: Create issue or discussion on GitHub

