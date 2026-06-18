# MountWizzard4 Improvement Plan – Developer Quick Reference

**TL;DR**: A 16-week plan to improve code quality, security, and developer experience across 8 dimensions.

---

## The 8 Areas of Improvement

```
1. PERFORMANCE         → 5-15% improvement in hotspots
2. ARCHITECTURE        → Better code organization
3. READABILITY         → Pythonic patterns, clearer code
4. MAINTAINABILITY     → Better documentation, easier changes
5. CI/CD PERFORMANCE   → 40% faster builds
6. SECURITY            → Vulnerability scanning, input validation
7. PYTHONIC STYLE      → Modern Python 3.11+ features
8. ANNOTATIONS         → Strict type checking (Mypy)
```

---

## Quick Timeline

```
Week 1-2   → Phase 1: Type System & Exceptions
Week 3-4   → Phase 2: Architecture Refactoring  
Week 5-6   → Phase 3: Pythonic Patterns & Performance
Week 7-8   → Phase 4: Documentation & Type Coverage
Week 9-10  → Phase 5: Testing Infrastructure
Week 11-12 → Phase 6: Security Hardening
Week 13-14 → Phase 7: CI/CD Optimization
Week 15-16 → Phase 8: Maintenance & Monitoring
```

---

## Phase 1: Foundation (Weeks 1-2)

### What We're Doing
- Adding `ParamSpec` to Worker class (better typing for functions)
- Creating custom exceptions (instead of generic `Exception`)
- Replacing `Any` types with specific types
- Setting up Mypy for type checking

### Key Files
- `src/mw4/base/tpool.py` – Worker class
- `src/mw4/base/exceptions.py` – NEW exception hierarchy
- `src/mw4/base/*.py` – Remove `Any` types

### Developer Actions
1. Review `mypy.ini` configuration
2. Understand ParamSpec and Protocols
3. Add type hints as you edit files
4. Use new exception types instead of generic Exception

### Success Criteria
- ✅ Mypy passes on base module
- ✅ Custom exceptions used throughout
- ✅ `Any` usage down 80%
- ✅ 100% test coverage maintained

---

## Phase 2: Architecture (Weeks 3-4)

### What We're Doing
- Breaking `src/mw4/base/` into organized sub-packages:
  - `core/` – Registry, device management
  - `threading/` – Workers, timers
  - `logging/` – Logger utilities
  - `protocols/` – Device protocols (INDI, ASCOM, etc.)
- Creating device protocol ABCs
- Updating all 256 files' import paths

### Key Changes
```python
# OLD
from mw4.base.deviceRegistry import DeviceRegistry

# NEW
from mw4.base.core.registry import DeviceRegistry
```

### Developer Actions
1. Update imports when file locations change
2. Use protocol ABCs when creating devices
3. Follow new sub-package structure for new files
4. Run tests after each import change

### Success Criteria
- ✅ No circular imports
- ✅ All 256 files import correctly
- ✅ ABCs properly implemented
- ✅ 100% test coverage maintained

---

## Phase 3: Pythonic & Performance (Weeks 5-6)

### What We're Doing
- Replace `os.path` with `pathlib.Path`
- Use f-strings exclusively (no `.format()` or `%`)
- Use list comprehensions instead of manual loops
- Implement context managers for resources
- Profile and optimize performance

### Code Changes

```python
# BEFORE
import os
home = os.path.expanduser("~")
config_dir = os.path.join(home, ".mw4")

# AFTER
from pathlib import Path
config_dir = Path.home() / ".mw4"
```

```python
# BEFORE
msg = "Device {} at {}".format(name, pos)

# AFTER
msg = f"Device {name} at {pos}"
```

```python
# BEFORE
result = []
for item in items:
    if item.active:
        result.append(item.process())

# AFTER
result = [item.process() for item in items if item.active]
```

### Developer Actions
1. Use pathlib for all file operations
2. Use f-strings exclusively
3. Use comprehensions and modern loops
4. Watch for performance regressions

### Success Criteria
- ✅ 0 `.format()` or `%` string formatting
- ✅ 0 `os.path` usage
- ✅ 5-15% performance improvement
- ✅ 100% test coverage maintained

---

## Phase 4: Documentation & Types (Weeks 7-8)

### What We're Doing
- Add docstrings to all modules (Google-style)
- Add Mypy to full codebase
- Document all public APIs
- Generate documentation site

### Docstring Format

```python
"""
Module: device_registry

Manages device registration and lifecycle.

This module provides:
- DeviceRegistry: Central device management
- DeviceEntry: Individual device tracking

Example:
    registry = DeviceRegistry(app)
    device = registry.createDevice('INDI', config)

Note:
    Thread-safe for concurrent access.
"""

class DeviceRegistry:
    """
    Central registry for all connected devices.
    
    Attributes:
        app: Parent application instance
        devices: Dictionary of registered devices
        
    Thread Safety:
        Thread-safe for concurrent access.
    """
    
    def createDevice(self, protocol: str, config: dict) -> Device:
        """
        Create and register a new device.
        
        Args:
            protocol: Device protocol (INDI, ASCOM, Alpaca)
            config: Device configuration dictionary
            
        Returns:
            Created Device instance
            
        Raises:
            ValueError: If protocol is unknown
            ConfigurationError: If config is invalid
        """
```

### Developer Actions
1. Write docstrings for all your code
2. Use Google-style format
3. Run `mypy` before committing
4. Document all public APIs

### Success Criteria
- ✅ 100% module docstrings
- ✅ Mypy passes on all modules
- ✅ Type coverage > 95%
- ✅ 100% test coverage maintained

---

## Phase 5: Testing (Weeks 9-10)

### What We're Doing
- Parallelize test execution with pytest-xdist
- Identify and fix flaky tests
- Add integration tests
- Add stress tests for long-running operations

### Running Tests Faster

```bash
# Run tests in parallel (before)
uv run pytest tests/unit_tests  # ~15 minutes

# Run tests in parallel (after)
uv run pytest tests/unit_tests -n auto  # ~9 minutes
```

### Developer Actions
1. Write deterministic tests (no randomness)
2. Use proper fixtures for setup/teardown
3. Avoid test interdependencies
4. Mark slow tests with `@pytest.mark.slow`

### Success Criteria
- ✅ Tests run 40% faster
- ✅ Flaky tests < 0.5%
- ✅ 100% test coverage maintained
- ✅ Integration tests for devices

---

## Phase 6: Security (Weeks 11-12)

### What We're Doing
- Add CVE scanning to CI/CD
- Create input validation framework
- Implement audit logging
- Review and harden device communication

### Key Changes
```python
# NEW: Input validation
from mw4.base.validation import validate_device_config

config = {"name": "mount1", "host": "192.168.1.1"}
validate_device_config(config)  # Raises if invalid

# NEW: Custom exceptions
try:
    device.connect()
except DeviceConnectionError as e:
    logger.error(f"Connection failed: {e}")
```

### Developer Actions
1. Validate all external inputs
2. Use specific exceptions, not generic `Exception`
3. Log security-relevant events
4. Sanitize sensitive data in logs

### Success Criteria
- ✅ CVE scanning in CI/CD
- ✅ All inputs validated
- ✅ Zero high-severity vulnerabilities
- ✅ Audit trail implemented

---

## Phase 7: CI/CD (Weeks 13-14)

### What We're Doing
- Optimize GitHub Actions workflows
- Add build caching
- Parallelize test execution
- Automate releases

### What Changes

```bash
# Before: Build takes 5m30s
# After: Build takes 3m20s (40% reduction)
```

### Developer Actions
1. Use cached dependencies
2. Commit `.github/workflows` changes carefully
3. Test release automation before using
4. Monitor CI/CD metrics

### Success Criteria
- ✅ Build time reduced 40%
- ✅ Build cache working
- ✅ Release automation functional
- ✅ All tests pass in CI

---

## Phase 8: Maintenance (Weeks 15-16)

### What We're Doing
- Set up quality metrics dashboard
- Write developer handbook
- Document architecture
- Create maintenance runbooks

### Developer Actions
1. Follow established patterns
2. Contribute to documentation
3. Share knowledge with team
4. Report issues and improvement ideas

### Success Criteria
- ✅ Documentation complete
- ✅ Quality metrics tracked
- ✅ Onboarding time reduced
- ✅ Patterns established

---

## Developer Responsibilities by Phase

### Phase 1
- [ ] Understand ParamSpec and Protocols
- [ ] Use new exception types
- [ ] Add type hints to your code
- [ ] Run Mypy locally

### Phase 2
- [ ] Update imports when modules move
- [ ] Use new package structure for new files
- [ ] Implement protocol ABCs if creating devices
- [ ] Test after each import change

### Phase 3
- [ ] Use pathlib for file operations
- [ ] Use f-strings exclusively
- [ ] Use comprehensions and modern loops
- [ ] Be aware of performance impact

### Phase 4
- [ ] Write Google-style docstrings
- [ ] Document all public APIs
- [ ] Add type hints everywhere
- [ ] Run Mypy before commit

### Phase 5
- [ ] Write deterministic tests
- [ ] Use proper fixtures
- [ ] Mark slow tests
- [ ] Avoid test interdependencies

### Phase 6
- [ ] Validate all external inputs
- [ ] Use custom exceptions
- [ ] Log security events
- [ ] Sanitize sensitive data

### Phase 7
- [ ] Use cached dependencies
- [ ] Follow CI/CD patterns
- [ ] Test before releasing
- [ ] Monitor metrics

### Phase 8
- [ ] Follow established patterns
- [ ] Contribute to documentation
- [ ] Share knowledge
- [ ] Suggest improvements

---

## Common Developer Questions

**Q: Does this break my code?**  
A: No. Each phase is validated with 100% test coverage. If something breaks, it's caught immediately.

**Q: How do I update imports?**  
A: We'll provide automated scripts. Review the changes, run tests, commit.

**Q: What's ParamSpec?**  
A: It's a new way to type generic functions. Like `def wrapper(*args, **kwargs)` but typed correctly.

**Q: Do I need to change my code right now?**  
A: Not immediately. But follow new patterns for new code. Old code will be updated gradually.

**Q: What if I disagree with a change?**  
A: Bring it up in weekly standups. All decisions are team decisions.

**Q: How do I report issues?**  
A: File an issue on GitHub. Include reproduction steps if applicable.

---

## Useful Commands

```bash
# Check type hints
mypy src/mw4/base --config-file mypy.ini

# Format code with Ruff
ruff format src/mw4/

# Lint with Ruff
ruff check src/mw4/

# Run tests
uv run pytest tests/unit_tests/

# Run tests in parallel
uv run pytest tests/unit_tests/ -n auto

# Check coverage
uv run pytest tests/unit_tests/ --cov=src/mw4

# Run only base tests
uv run pytest tests/unit_tests/base/

# Run with verbose output
uv run pytest tests/unit_tests/ -v
```

---

## Key Resources

1. **IMPROVEMENT_PLAN.md** – Full 16-week plan
2. **IMPLEMENTATION_ROADMAP.md** – Detailed task breakdown
3. **IMPROVEMENT_PLAN_EXECUTIVE_SUMMARY.md** – Business case
4. **Python 3.11 Features** – https://docs.python.org/3.11/whatsnew/
5. **PEP 484** (Type Hints) – https://peps.python.org/pep-0484/
6. **PEP 612** (ParamSpec) – https://peps.python.org/pep-0612/
7. **Google Python Style Guide** – https://google.github.io/styleguide/pyguide.html
8. **Mypy Documentation** – https://mypy.readthedocs.io/

---

## Important Dates

- **Week 1** – Phase 1 starts
- **Week 3** – Phase 2 starts
- **Week 5** – Phase 3 starts
- **Week 7** – Phase 4 starts
- **Week 9** – Phase 5 starts
- **Week 11** – Phase 6 starts
- **Week 13** – Phase 7 starts
- **Week 15** – Phase 8 starts
- **Week 16** – Plan complete

---

## Need Help?

- **Questions**: Ask in standup or Slack
- **Issues**: File on GitHub
- **Ideas**: Discuss in retrospectives
- **Blockers**: Escalate immediately

---

**Last Updated**: June 18, 2026  
**For Questions**: Create GitHub Issue or Discussion  
**Status**: Ready for Implementation

