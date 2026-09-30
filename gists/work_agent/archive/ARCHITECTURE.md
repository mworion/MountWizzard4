# MountWizzard4 Project Architecture

## Overview

MountWizzard4 is a sophisticated Python desktop application for controlling **10micron telescope mounts**. It follows a layered architecture pattern with clear separation of concerns between the GUI, business logic, and infrastructure layers.

---

## Architecture Layers

### 1. **Presentation Layer (GUI)**
Located in: `../../src/mw4/gui`

**Purpose**: Provides the user interface using PySide6 (Qt6) and PyQtGraph.

**Components**:
- **Main Window** (`mainWindow/`, `mainApp.py`)
  - Central application container
  - Manages multiple tabs and dialogs
  
- **External Windows** (`extWindows/`)
  - Separate application windows for specialized functions
  
- **Device Tabs** (`mainWaddon/`)
  - Camera control
  - Dome control
  - Telescope/Mount control
  - Environment monitoring
  - Satellite tracking
  
- **Tool Tabs** (`mainWaddon/`)
  - Profile management
  - Imaging workflows
  - Model building
  - Plate solving
  - Photometry
  
- **GUI Utilities**
  - `utilities/`: Helper functions and widgets
  - `styles/`: Qt stylesheets and themes
  - `widgets/`: Auto-generated Qt Designer widgets

---

### 2. **Business Logic Layer**
Located in: `../../src/mw4/logic`

**Purpose**: Implements device control logic and astronomical calculations.

**Device Categories**:

#### Imaging Devices
- **Camera** - Image acquisition and control
- **Focuser** - Focus position management
- **Filter Wheel** - Filter selection

#### Observatory Control
- **Dome** - Dome rotation and control
- **Cover** - Dust cover management
- **Power Switch** - Equipment power control

#### Environmental Systems
- **Environment** - Weather, temperature, humidity monitoring
- **Satellites** - Satellite tracking using SGP4
- **Measurement** - Observational data collection

#### Image Processing & Analysis
- **Plate Solving** - Astrometric solving (using external solvers)
- **Photometry** - Stellar photometry calculations
- **FITS/XISF** - Image file I/O (FITS and XISF formats)

#### Mount & Telescope Analysis
- **Telescope** - Telescope control and coordination
- **Model Building** - Mount model computation
- **Build Data** - Model calibration data management

#### Additional Logic Modules
- **driverHandling/** - INDI/ALPACA driver management
- **databaseProcessing/** - Data persistence and queries
- **remote/** - Remote protocol handlers
- **profiles/** - User profile configuration

---

### 3. **Infrastructure & Foundation Layer**
Located in: `../../src/mw4/base`

**Purpose**: Provides core services and utilities for the entire application.

#### Device Communication
- **INDI Protocol** (`indiClass.py`, `indiClassAddOns.py`)
  - Uses `indipyclient` library
  - Primary protocol for Linux/Mac astronomical equipment
  
- **ALPACA/ASCOM** (`alpacaClass.py`, `ascomClass.py`)
  - Windows-based standard
  - Fallback for ASCOM-compatible devices

#### Core Services
- **Thread Pool** (`tpool.py`)
  - Manages worker threads for long-running operations
  - Prevents GUI blocking
  
- **Signals & Slots** (`signalsDevices.py`)
  - Qt-based inter-module communication
  - Thread-safe event propagation
  
- **Device Registry** (`deviceRegistry.py`)
  - Central device management
  - Device discovery and lifecycle
  
- **Device Entry** (`deviceEntry.py`)
  - Generic device abstraction
  - Common interface for all devices

#### Data & Configuration Management
- **Configuration** (`packageConfig.py`)
  - Application settings (YAML/JSON)
  - User preferences
  
- **Database Processing** (`databaseProcessing/`)
  - Data persistence layer
  - Measurement and calibration storage

#### Utilities & Support
- **Logger** (`loggerMW.py`)
  - Centralized logging
  
- **Time Manager** (`timeManager.py`)
  - Time zone and UTC handling
  
- **Transform Utilities** (`transform.py`)
  - Coordinate transformations
  
- **Audio Manager** (`audioManager.py`)
  - Alert and notification sounds
  
- **Bootstrap** (`bootstrap.py`)
  - Application initialization

---

### 4. **Mount Control Module (Special)**
Located in: `../../src/mw4/mountcontrol`

**Purpose**: Dedicated module for 10micron mount communication.

**Responsibilities**:
- **10micron Mount Protocol**
  - Direct socket communication
  - Proprietary command set implementation
  
- **Connection Handshake**
  - Mount discovery
  - Session initialization
  - Authentication
  
- **Mount Commands**
  - Position queries
  - Slewing operations
  - Tracking control
  
- **Status & Telemetry**
  - Real-time position reporting
  - System status monitoring
  
- **Model Management**
  - Mount model upload/download
  - Calibration data handling

---

## External Dependencies & Integration

### Astronomy Libraries
- **Astropy** - Coordinate systems, time calculations
- **Skyfield** - Ephemerides, satellite tracking
- **SGP4** - Satellite orbit prediction
- **PyERFA** - Earth rotation angles

### Image Processing
- **NumPy** - Numerical computations
- **SciPy** - Scientific algorithms
- **OpenCV (headless)** - Advanced image processing
- **Photutils** - Astronomical photometry
- **SEP** - Source extraction

### Image Formats
- **FITS** - Flexible Image Transport System (Astropy)
- **XISF** - eXtensible Image Serialization Format

### Networking & Protocols
- **WebSocket** (`websocket-client`)
- **REST** (via `requests`)
- **HID** (`hidapi`)
- **Ethernet** utilities

### Desktop Framework
- **PySide6** (Qt 6) - Core GUI framework
- **PyQtGraph** - Scientific visualization
- **QImage2ndarray** - Image array conversion

### Data Formats
- **PyYAML** - Configuration serialization
- **JSON** - Data exchange
- **Python-dateutil** - Date/time handling

---

## Data Flow Patterns

### Typical Device Control Flow
```
GUI Tab (user interaction)
  ↓
Device Logic Class
  ↓
Thread Pool Worker (if long-running)
  ↓
Infrastructure Services (Config, Device Registry)
  ↓
Protocol Handler (INDI, ALPACA, or Direct)
  ↓
External Device
  ↓
Status Signals back to GUI
```

### Astronomical Calculation Flow
```
GUI Tab (parameters)
  ↓
Logic Module (Plate Solve, Photometry, etc.)
  ↓
Astronomy Library (Astropy, Skyfield)
  ↓
Result signals to GUI
```

### Mount Communication Flow
```
GUI Mount Tab
  ↓
Telescope Logic
  ↓
Mount Control Module
  ↓
10micron Mount Protocol
  ↓
Mount Hardware
```

---

## Communication Patterns

### Asynchronous Operations
- All I/O-bound operations run on thread pool workers
- Results communicated via Qt Signals & Slots
- GUI remains responsive

### Configuration Management
- Centralized in `packageConfig`
- Persistent storage via YAML/JSON
- Real-time updates to listeners

### Device Discovery
- Device Registry maintains live device list
- Hot-plug support (devices can be added/removed at runtime)
- Health monitoring and reconnection logic

---

## Key Design Principles

1. **Loose Coupling**: GUI tabs are independent; they communicate only through signals
2. **Layered Architecture**: Clear separation between GUI, logic, and infrastructure
3. **Thread Safety**: Long operations moved to thread pool; signals for communication
4. **Reusability**: Common functionality in `base/` layer accessible to all modules
5. **Extensibility**: Device architecture supports new hardware easily
6. **Testing**: Comprehensive unit test coverage (100%) with clear module boundaries

---

## Build & Deployment

- **Build System**: `uv` / `uv_build`
- **Python Version**: 3.12+ (compatible with 3.12, 3.13, 3.14)
- **Platform Support**: macOS, Windows, Linux
- **Entry Points**: Multiple CLI entry points (`mw4`, `mw`, `MW`, etc.)

---

## File Organization Reference

```
src/mw4/
├── __main__.py              # Entry point
├── cli.py                   # Command-line interface
├── mainApp.py              # Main application class
├── loader.py               # Resource loading
│
├── gui/                    # Presentation Layer
│   ├── mainWindow/         # Main window components
│   ├── mainWaddon/         # Device and tool tabs
│   ├── extWindows/         # External dialogs
│   ├── utilities/          # GUI helpers
│   ├── styles/             # CSS/themes
│   └── widgets/            # Qt Designer outputs
│
├── logic/                  # Business Logic Layer
│   ├── camera/             # Camera device
│   ├── dome/               # Dome device
│   ├── telescope/          # Telescope control
│   ├── plateSolve/         # Astrometric solving
│   ├── photometry/         # Stellar photometry
│   ├── environment/        # Weather monitoring
│   ├── satellites/         # Satellite tracking
│   ├── fits/               # FITS I/O
│   ├── modelBuild/         # Mount model building
│   └── [other devices]
│
├── base/                   # Infrastructure Layer
│   ├── indiClass.py        # INDI protocol
│   ├── alpacaClass.py      # ALPACA/ASCOM
│   ├── deviceRegistry.py   # Device management
│   ├── tpool.py            # Thread pool
│   ├── signalsDevices.py   # Signal definitions
│   ├── packageConfig.py    # Configuration
│   ├── loggerMW.py         # Logging
│   └── [other utilities]
│
└── mountcontrol/           # Mount Control Module
    ├── MountControl.py     # Main controller
    └── [mount-specific]
```

---

## Testing Strategy

- **Location**: `../../tests/unit_tests`
- **Structure**: Mirrors `../../src/mw4` layout
- **Framework**: pytest, pytest-qt
- **Coverage**: 100% required
- **Markers**: `@pytest.mark.gui`, `@pytest.mark.logic`, etc.


