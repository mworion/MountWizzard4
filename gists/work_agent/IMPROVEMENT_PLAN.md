# MountWizzard4 – Stepwise Improvement Plan
**Version**: 1.0  
**Created**: June 18, 2026  
**Scope**: Performance, Architecture, Readability, Maintainability, CI/CD, Security, Pythonic Style, Type Annotations

---

## Executive Summary

**Current State**:
- 47,936 lines of code (256 Python files)
- 50,184 lines of test code (204 test files)
- 100% test coverage maintained
- Python 3.13 compatibility
- Solid architectural foundation with business logic/GUI separation

**Goal**: Elevate the codebase to production-grade standards through systematic improvements in performance, security, maintainability, and developer experience.

---

## Phase 1: Foundation & Type System (Weeks 1–2)

### 1.1 Type Annotation Audit & ParamSpec Usage

**Objective**: Replace generic `Any` types with specific types and improve generic function typing.

**Status Check**:
- 20+ files currently import `Any` (basemodule files identified)
- Missing ParamSpec for generic worker functions
- Queue and Signal types lack proper generic parameters

**Implementation Steps**:
1. **Priority 1: Core Threading Module** (`src/mw4/base/tpool.py`)
   - Implement `ParamSpec` for `Worker` class to capture function signatures
   - Add return type annotations to `runFunction()`
   - Add generic types for `QRunnable` and `Signal` emissions

2. **Priority 2: Base Device Classes** (`src/mw4/base/*.py`)
   - Replace `Any` in `alpacaClass.py`, `indiClass.py`, `ascomClass.py`
   - Use `Protocol` for device interface definitions
   - Add TypedDict for configuration structures
   - Type hint all `self.parent`, `self.app` references with Protocol

3. **Priority 3: Logic & GUI Communication**
   - Type hint `queue.Queue` with specific message types
   - Define return types for all signal callbacks
   - Create TypedDict for common data structures

**Tests Required**:
- Unit tests validating type hints with `mypy` or similar static analysis
- Runtime tests for type correctness (sample coverage)
- No coverage decrease

**Deliverables**:
- Updated worker classes with ParamSpec
- Device interface Protocols
- Mypy configuration for CI

---

### 1.2 Custom Exception Hierarchy

**Objective**: Replace generic `Exception` catching with specialized error types.

**Current Issues**:
- Broad exception catching in `bootstrap.py`, `alpacaAscomCommon.py`
- Loss of error context and debugging information
- Difficult to handle different failure modes distinctly

**Implementation Steps**:
1. Create `src/mw4/base/exceptions.py`:
   ```python
   - MountWizzardException (base)
   - DeviceConnectionError
   - ProtocolCommunicationError
   - ConfigurationError
   - FileIOError
   - ThreadPoolError
   - ValidationError
   ```

2. Update error handling in:
   - `src/mw4/base/alpacaAscomCommon.py` (connectDevice)
   - `src/mw4/base/bootstrap.py` (file operations)
   - Device protocol classes (indiClass, ascomClass)
   - Mount control modules

3. Log exception chains with context

**Tests Required**:
- Test each exception type is raised in appropriate scenarios
- Test exception catching is specific (not catching parent Exception)
- 100% coverage of error paths

**Deliverables**:
- Exceptions module with documentation
- Updated try/except blocks throughout codebase
- Error handling consistency guidelines

---

## Phase 2: Architecture Refactoring (Weeks 3–4)

### 2.1 Base Module Sub-package Reorganization

**Objective**: Break down `src/mw4/base/` into logical sub-packages for better organization and reduced coupling.

**Current Structure**:
```
src/mw4/base/
├── alpacaAscomCommon.py
├── alpacaClass.py
├── ascomClass.py
├── bootstrap.py
├── deviceEntry.py
├── deviceRegistry.py
├── driverDataClass.py
├── exceptions.py (new)
├── indiClass.py
├── loggerMW.py
├── packageConfig.py
├── sgproClass.py
├── timerManager.py
└── tpool.py
```

**Proposed Structure**:
```
src/mw4/base/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── registry.py (from deviceRegistry.py)
│   ├── entry.py (from deviceEntry.py)
│   └── drivers.py (from driverDataClass.py)
├── threading/
│   ├── __init__.py
│   ├── worker.py (from tpool.py)
│   └── timers.py (from timerManager.py)
├── logging/
│   ├── __init__.py
│   └── logger.py (from loggerMW.py)
├── protocols/
│   ├── __init__.py
│   ├── common.py (from alpacaAscomCommon.py)
│   ├── indi.py (from indiClass.py)
│   ├── ascom.py (from ascomClass.py)
│   ├── alpaca.py (from alpacaClass.py)
│   └── sgpro.py (from sgproClass.py)
├── bootstrap.py (unchanged – entry point)
├── exceptions.py (new)
├── packageConfig.py (unchanged)
└── __all__.py (public API)
```

**Implementation Steps**:
1. Create new sub-package directories with __init__.py files
2. Move files to appropriate locations
3. Update all imports throughout codebase (256 files potentially affected)
4. Create clear public APIs via `__all__` exports
5. Add docstrings to explain sub-package purposes

**Validation**:
- All imports resolve correctly
- No circular dependencies
- Same number of passing tests
- 100% coverage maintained

**Testing Strategy**:
- Run full test suite after each major file move
- Update import paths in all test files (204 test files)
- Validate no performance regression

**Deliverables**:
- Reorganized base module
- Import path update documentation
- Dependency graph visualization

---

### 2.2 Device Protocol Abstract Base Classes

**Objective**: Define consistent interfaces for different device protocols.

**Implementation Steps**:
1. Create `src/mw4/base/protocols/__init__.py` with ABCs:
   ```python
   - DeviceBase (abstract)
     - startCommunication()
     - stopCommunication()
     - pollData()
     - getName()
   
   - IndiDeviceProtocol
   - AscomDeviceProtocol
   - AlpacaDeviceProtocol
   ```

2. Update existing classes to inherit from ABCs
3. Implement `__init_subclass__()` for validation
4. Add protocol validation in device factory

**Benefits**:
- Enforces consistent method signatures
- Improves IDE autocomplete
- Better static type checking
- Reduces duck typing errors

**Tests Required**:
- Test each protocol implementation against ABC
- Test factory creates correct protocol instances
- 100% coverage of ABC methods

---

## Phase 3: Code Quality & Pythonic Patterns (Weeks 5–6)

### 3.1 Pythonic Code Improvements

**Objective**: Modernize code using Python 3.11+ features and idiomatic patterns.

**Areas to Address**:

#### A. String & Path Handling
- Replace string path manipulations with `pathlib.Path`
- Update all `os.path` calls to use `pathlib`
- Use f-strings exclusively (no `%` or `.format()`)

**Files to Update**:
- `src/mw4/base/bootstrap.py` (extractDataFiles)
- `src/mw4/base/packageConfig.py`
- All device configuration loaders

#### B. Loop & Iterator Improvements
- Replace manual loops with `enumerate()`, `zip()`
- Use list/dict/set comprehensions where appropriate
- Replace `filter()` and `map()` with comprehensions

#### C. Context Managers
- `Worker` class: implement `__enter__`/`__exit__`
- Database operations: use `contextlib.closing()`
- File operations: use context managers

#### D. Constants & Enums
- Convert feature flags to `Enum` or use `Final`
- Group related constants in dataclasses
- Use `|` operator for flag combinations (Python 3.10+)

**Test Strategy**:
- Linting with Ruff to enforce patterns
- Performance benchmarks before/after
- 100% coverage maintained

**Deliverables**:
- Updated modules using modern Python patterns
- Ruff configuration for style enforcement
- Before/after comparison document

---

### 3.2 Performance Optimization

**Objective**: Identify and optimize bottlenecks without sacrificing readability.

**Profiling Strategy**:

1. **Identify hotspots**:
   - Profile GUI rendering (PyQtGraph charts, image updates)
   - Profile device polling loops
   - Profile image processing (OpenCV operations)
   - Profile file I/O (FITS/XISF reading)

2. **Optimization Areas**:
   - **GUI**: Cache computed layouts, use `QTimer` for batched updates
   - **Polling**: Optimize device polling intervals, use async patterns
   - **Image**: Vectorize NumPy operations, preallocate arrays
   - **I/O**: Use memory-mapped files, implement lazy loading

3. **Metrics to Track**:
   - Memory usage per component
   - CPU utilization during imaging workflows
   - UI responsiveness (frame rate)
   - Startup time

**Implementation**:
- Add performance benchmarks to test suite
- Create `src/mw4/base/performance.py` for decorators
- Document optimization decisions

**CI/CD Integration**:
- Track performance metrics in CI
- Alert on regressions > 5%

**Tests Required**:
- Benchmark tests (marked as slow)
- Memory leak detection
- 100% coverage maintained

---

### 3.3 Resource Management & Cleanup

**Objective**: Ensure proper resource cleanup and prevent leaks.

**Implementation Steps**:

1. **Worker Thread Management**:
   - Implement context manager for `Worker` class
   - Ensure thread cleanup on exception
   - Add timeout handling

2. **Device Communication**:
   - Implement proper disconnect handlers
   - Ensure socket/connection cleanup
   - Test edge cases (network failures)

3. **Memory**:
   - WeakRef for callbacks
   - Image buffer cleanup
   - Cache expiration

**Testing**:
- Memory profiler tests
- Long-running stability tests (12+ hour runs)
- Resource exhaustion tests

---

## Phase 4: Documentation & Type Coverage (Weeks 7–8)

### 4.1 Type Checking with Mypy

**Objective**: Achieve strict type checking compliance.

**Setup**:
1. Create `mypy.ini`:
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
   ```

2. Add Mypy to CI/CD pipeline
3. Phase 1: Check base module
4. Phase 2: Check logic module
5. Phase 3: Check GUI module (excluding auto-generated widgets)

**Gradual Typing Strategy**:
- Start with `py.typed` marker file
- Phase in `disallow_untyped_defs` module by module
- Document any necessary `type: ignore` comments

**Deliverables**:
- Mypy CI check passing
- Type stubs for third-party libraries if needed
- Type coverage report

---

### 4.2 Documentation Standards

**Objective**: Improve codebase documentation for maintainability.

**Implementation**:

1. **Module-level Docstrings**:
   - Every module gets a description
   - Document public API
   - Include usage examples where applicable

2. **Class Docstrings**:
   - Use Google-style docstrings
   - Document all public methods
   - Include type hints in docstrings as backup

3. **Complex Algorithms**:
   - Document algorithm name/reference
   - Explain non-obvious logic
   - Link to relevant specs/standards

4. **API Reference**:
   - Auto-generate from docstrings
   - Host on documentation site

**Tools**:
- Sphinx for auto-documentation
- pdoc for quick reference
- MkDocs for hosting

**Tests**:
- Docstring coverage reporting
- Example code validation (doctest)

---

## Phase 5: Testing & Coverage (Weeks 9–10)

### 5.1 Test Infrastructure Improvements

**Objective**: Enhance test quality and reduce CI/CD time.

**Current State**:
- 204 test files, 50,184 lines of test code
- 100% coverage maintained
- 4 parallel jobs in macOS CI

**Improvements**:

1. **Test Organization**:
   - Group slow tests (mark with `@pytest.mark.slow`)
   - Separate GUI tests from logic tests
   - Create integration test suite

2. **CI/CD Parallelization**:
   - Use `pytest-xdist` for parallel execution
   - Balance test distribution across workers
   - Target 50% time reduction

3. **Coverage Enhancement**:
   - Identify untested edge cases
   - Add tests for error paths
   - Test Windows-specific code on Windows

4. **Test Data Management**:
   - Separate test fixtures from test data
   - Use factories for complex objects
   - Document test data dependencies

**Metrics**:
- Test execution time per module
- Coverage by module
- Flake rate (flaky tests)

**Deliverables**:
- Optimized test suite
- CI configuration with parallelization
- Test quality metrics dashboard

---

### 5.2 Integration & Stress Tests

**Objective**: Ensure robustness under real-world conditions.

**Test Scenarios**:

1. **Device Communication**:
   - Simulate network failures
   - Test reconnection logic
   - Test timeout handling

2. **GUI Stress**:
   - Rapid widget creation/destruction
   - High-frequency signal emissions
   - Memory under sustained use

3. **Long-running Operations**:
   - Imaging sequences (12+ hours)
   - Mount tracking stability
   - Database growth

**Framework**:
- Use `pytest` fixtures for setup
- Implement custom assertions for astronomical data
- Use `hypothesis` for property-based testing

---

## Phase 6: Security Hardening (Weeks 11–12)

### 6.1 Dependency Vulnerability Scanning

**Objective**: Proactively identify and patch security vulnerabilities.

**Implementation**:

1. **Setup Scanning**:
   - Add `safety check` to CI (checks known CVEs)
   - Pin exact dependency versions
   - Regular dependency updates (monthly)

2. **Current Dependencies** (Key Security-Sensitive):
   - `requests==2.34.2` (HTTP library)
   - `websocket-client==1.9.0` (WebSocket)
   - `pywin32==311` (Windows integration)
   - `pyyaml==6.0.3` (Configuration parsing)

3. **Update Strategy**:
   - Automate security patches with Dependabot
   - Test each update before merging
   - Document breaking changes

**Deliverables**:
- CVE scanning in CI
- Dependency audit report
- Security patch workflow

---

### 6.2 Input Validation & Sanitization

**Objective**: Prevent injection attacks and data corruption.

**Areas to Secure**:

1. **Network Input**:
   - Validate INDI/Alpaca protocol messages
   - Sanitize HTTP responses
   - Validate WebSocket frames

2. **File Input**:
   - Validate FITS headers
   - Validate XISF files
   - Validate configuration YAML/JSON

3. **User Input**:
   - GUI field validation
   - Command injection prevention
   - Path traversal prevention

**Implementation**:
- Create validation module: `src/mw4/base/validation.py`
- Define validators for common types
- Use dataclass validation with `__post_init__`

**Tests**:
- Malformed input tests
- Fuzzing tests (limited)
- Injection attack scenarios

---

### 6.3 Logging & Audit Trail

**Objective**: Maintain security audit trail without logging sensitive data.

**Implementation**:

1. **Sensitive Data**:
   - Mask passwords, tokens
   - Scrub coordinates in certain contexts
   - Filter API keys

2. **Audit Logging**:
   - Log device connections/disconnections
   - Log configuration changes
   - Log error conditions
   - Include timestamp, user, source

3. **Log Retention**:
   - Rotate logs (e.g., daily)
   - Retention policy (e.g., 30 days)
   - Secure archival

**Configuration**:
- Add audit logging to `loggerMW.py`
- Create log formatter for sensitive data
- Document logging best practices

---

## Phase 7: CI/CD Optimization (Weeks 13–14)

### 7.1 Workflow Optimization

**Objective**: Reduce CI/CD pipeline execution time and improve reliability.

**Current State**:
- Separate workflows for macOS, Ubuntu, Windows
- Multiple test groups to parallelize
- Build once, test multiple times

**Improvements**:

1. **Build Caching**:
   - Cache Python dependencies
   - Cache built wheels
   - Use GitHub Actions cache

2. **Test Distribution**:
   - Use `pytest-xdist` for parallel execution
   - Balance test load across workers
   - Run flaky tests separately

3. **Conditional Execution**:
   - Skip tests if only docs changed
   - Skip Windows tests on non-Windows
   - Skip GUI tests if only logic changed

4. **Artifact Management**:
   - Only keep latest artifacts
   - Clean old artifacts automatically

**Target**: 40% reduction in total CI time

**Deliverables**:
- Updated GitHub Actions workflows
- Cache strategy documentation
- Performance metrics before/after

---

### 7.2 Release Automation

**Objective**: Streamline release process with automated checks.

**Implementation**:

1. **Pre-release Checks**:
   - Version number consistency
   - Changelog entry
   - All tests passing
   - Coverage maintained at 100%
   - No security vulnerabilities

2. **Release Process**:
   - Create GitHub release with changelog
   - Build and upload to PyPI
   - Generate documentation
   - Update version numbers

3. **Post-release**:
   - Verify PyPI package
   - Test installation
   - Update version to next dev

**Tools**:
- Use `invoke` or GitHub Actions
- Automate with release bot

---

## Phase 8: Maintenance & Monitoring (Weeks 15–16)

### 8.1 Quality Metrics Dashboard

**Objective**: Track code quality over time.

**Metrics to Track**:
- Test coverage (target: 100%)
- Code complexity (max: 10, aim for < 8)
- Type check success rate
- Security vulnerability count
- Documentation coverage
- Performance benchmarks

**Tools**:
- Codecov for coverage tracking
- Code quality services (Codacy, CodeFactor)
- Custom metrics dashboards

---

### 8.2 Continuous Learning & Documentation

**Objective**: Document improvements and establish maintenance guidelines.

**Deliverables**:

1. **Architecture Guide**:
   - Module dependency diagram
   - Data flow diagrams
   - Design patterns used

2. **Developer Handbook**:
   - Onboarding guide
   - Coding standards
   - Common tasks (adding new device, new tab, etc.)

3. **Performance Guide**:
   - Profiling instructions
   - Optimization techniques
   - Common bottlenecks

4. **Security Guidelines**:
   - Input validation patterns
   - Sensitive data handling
   - Incident response

---

## Implementation Timeline

| Phase | Duration | Key Deliverables | Stakeholders |
|-------|----------|------------------|--------------|
| 1 | Weeks 1–2 | Type system, exceptions | Core developers |
| 2 | Weeks 3–4 | Base module refactor | All developers |
| 3 | Weeks 5–6 | Pythonic improvements | All developers |
| 4 | Weeks 7–8 | Documentation, Mypy | All developers, docs team |
| 5 | Weeks 9–10 | Test improvements | QA, CI/CD |
| 6 | Weeks 11–12 | Security hardening | Security team, all developers |
| 7 | Weeks 13–14 | CI/CD optimization | DevOps, release team |
| 8 | Weeks 15–16 | Monitoring, guidelines | All teams |

**Total Duration**: ~4 months
**Estimated Effort**: 640–800 person-hours

---

## Success Criteria

### Phase 1 (Type System)
- [ ] ParamSpec usage in threading module
- [ ] All 20+ `Any` imports reduced by 80%
- [ ] Mypy passes on core modules
- [ ] Custom exception hierarchy in place
- [ ] 100% coverage maintained

### Phase 2 (Architecture)
- [ ] Base module reorganized into 5 sub-packages
- [ ] All imports updated (256 files)
- [ ] Device ABCs implemented
- [ ] No circular dependencies
- [ ] 100% coverage maintained
- [ ] No performance regression

### Phase 3 (Pythonic & Performance)
- [ ] All `os.path` replaced with `pathlib`
- [ ] All string formatting uses f-strings
- [ ] Performance benchmarks established
- [ ] Worker class implements context manager
- [ ] 5%–15% performance improvement in hotspots

### Phase 4 (Documentation)
- [ ] 100% module docstring coverage
- [ ] Mypy strict mode passing
- [ ] All public APIs documented
- [ ] Type coverage > 95%

### Phase 5 (Testing)
- [ ] CI/CD time reduced 40%
- [ ] 100% coverage maintained
- [ ] Flaky test count < 1%
- [ ] Integration tests for device protocols

### Phase 6 (Security)
- [ ] CVE scanning in CI
- [ ] Input validation module created
- [ ] Zero high-severity vulnerabilities
- [ ] Audit logging implemented

### Phase 7 (CI/CD)
- [ ] GitHub Actions workflows optimized
- [ ] Build cache in place
- [ ] Release automation working
- [ ] 40% faster CI/CD

### Phase 8 (Maintenance)
- [ ] Quality metrics dashboard
- [ ] Developer handbook completed
- [ ] Architecture documentation
- [ ] Maintenance runbooks

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Breaking changes in refactoring | High | Extensive testing, gradual rollout, backward compatibility layer |
| Performance regression | High | Benchmarking, profiling, performance gates in CI |
| Test flakiness | Medium | Increase test isolation, use proper fixtures, CI retries |
| Type checking too strict | Medium | Gradual phase-in, `type: ignore` for justified cases |
| Team capacity | High | Prioritize high-impact items, parallelize work |
| Dependency updates | Medium | Automated testing, security scanning, staged rollout |

---

## Dependencies & Prerequisites

1. **Team Skills**:
   - Proficiency with Python 3.11+ features
   - Understanding of type systems (PEP 484, 585, 604, 646)
   - Qt/PySide6 knowledge for GUI team
   - DevOps knowledge for CI/CD team

2. **Tools**:
   - Ruff (already configured)
   - Mypy or Pyright
   - pytest with plugins
   - GitHub Actions
   - Dependabot or similar

3. **Access**:
   - Full repository access
   - CI/CD pipeline modification
   - Package repository (PyPI)

---

## Review & Adjustment

- **Monthly Review**: Track progress against timeline
- **Sprint Planning**: Allocate 30% of capacity to this plan
- **Feedback Loop**: Gather developer feedback on changes
- **Quarterly Assessment**: Evaluate success metrics

---

## Appendix: Quick Reference

### Python 3.11+ Features to Leverage
- `ParamSpec` (PEP 612) for generic functions
- Match statements (PEP 634) for protocol routing
- Type union syntax `X | Y` (PEP 604)
- Variadic generics (PEP 646)
- Dataclass improvements

### Recommended Tools
- **Linting**: Ruff (already in use)
- **Type Checking**: Mypy or Pyright
- **Testing**: pytest, pytest-cov, pytest-xdist, hypothesis
- **Security**: safety, bandit, Dependabot
- **Documentation**: Sphinx, Google-style docstrings
- **Performance**: py-spy, memory_profiler

### References
- PEP 484: Type Hints
- PEP 612: ParamSpec
- PEP 634: Structural Pattern Matching
- PEP 604: Type Union Syntax
- Ruff Linter Documentation
- Mypy Documentation

---

## Next Steps

1. **Week 0**: Review and approve plan with team
2. **Week 1**: Create feature branch for Phase 1
3. **Weeks 1–2**: Execute Phase 1 with daily standups
4. **End of Week 2**: Team retrospective and Phase 2 planning
5. Continue iteratively through all phases

---

**Document Prepared By**: GitHub Copilot  
**Last Updated**: June 18, 2026  
**Status**: Ready for Implementation  
**Approval Required**: Yes

