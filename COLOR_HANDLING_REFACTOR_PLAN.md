# Color Handling Refactor Plan

## Executive Summary

The color system in MountWizzard4 currently uses a mixed approach:
- Base color properties return **list[int]** (RGBA tuples): `M_PRIM`, `M_SEC`, etc.
- String variants return **str** (rgba format): `M_PRIMs` (rgba string), `M_PRIMa` (RGBA with alpha), `M_PRIMas` (rgba string with alpha)
- Dynamic string conversions happen in `replaceColor()` and `renderStyle()` methods

This plan consolidates color handling into a single, consistent approach using RGB lists and removes string return values.

---

## Current System Analysis

### Color Property Suffixes

| Suffix | Type | Returns | Example |
|--------|------|---------|---------|
| (none) | Base | `list[int]` | `M_PRIM` → `[32, 144, 192, 255]` |
| `a` | With Alpha | `list[int]` | `M_PRIMa` → `[32, 144, 192, 255]` (alpha applied) |
| `s` | String | `str` | `M_PRIMs` → `"rgba(32, 144, 192, 255)"` |
| `as` | String+Alpha | `str` | `M_PRIMas` → `"rgba(32, 144, 192, 255)"` |

### Current Usages

**String Properties (27 usages):**
- `M_PRIMas`, `M_PRIM1as`, `M_PRIM2as`, `M_PRIM3as`, `M_PRIM4as` - setStyleSheet background colors (5)
- `M_PRIMa`, `M_YELLOWa`, `M_YELLOW1a`, `M_REDa`, `M_RED1a`, `M_PINKa`, `M_PINK1a` - pyqtgraph color params (18)
- Font HTML color tags - `M_PRIMa` (1)

**RGB Tuple Unpacking (many usages):**
- `QColor(*self.M_PRIM)` pattern for Qt/3D widgets
- pg.mkPen/mkBrush with list colors

**Dynamic String Conversion (rare):**
- `replaceColor()` → produces `"rgba(...)"` strings for stylesheet injection
- `renderStyle()` → processes stylesheets with color replacements

---

## Problems with Current System

### 1. **Type Inconsistency**
- Same property name with different suffixes returns different types
- PyQt and 3D engine functions need QColor objects, not strings
- Strings only work in CSS/HTML contexts (setStyleSheet, font color tags)

### 2. **String Format Issues**
- Current format: `"rgba(32, 144, 192, 255)"` is invalid CSS
- Correct CSS format: `"rgba(32, 144, 192, 1.0)"` (normalized alpha 0-1)
- or: `"rgb(32, 144, 192)"` and handle alpha separately

### 3. **Hardcoded Alpha Logic**
- Alpha modification scattered across multiple properties
- `transparency` field affects both `a` and `as` variants inconsistently
- No clear contract for which properties apply transparency

### 4. **CSS/Stylesheet Awkwardness**
- `replaceColor()` tries to inject rgba strings into CSS
- PyQt setStyleSheet accepts CSS colors, but current format is invalid
- Better to use QSS properties or HTML color names/hex

### 5. **Testing Complexity**
- Tests fail because string format changed from hex to rgba
- setStyleSheet() with invalid rgba strings doesn't render properly

---

## Proposed Solution

### Phase 1: Consolidate to RGB Lists (Immediate)

**Remove string properties entirely:**
- Delete `M_*s` and `M_*as` property variants from `__getattr__`
- Keep only base colors (`M_PRIM`, `M_SEC`, etc.) as `list[int]`
- Keep alpha variants (`M_PRIMa`, `M_SECa`) as `list[int]` with transparency applied

**Update all usages:**

1. **CSS/setStyleSheet cases** → Convert to hex format
   ```python
   # Before
   widget.setStyleSheet(f"background-color: {self.M_PRIMas};")
   
   # After
   color_hex = self.rgb2hex(self.M_PRIM)
   widget.setStyleSheet(f"background-color: {color_hex};")
   ```

2. **pyqtgraph and Qt functions** → Use rgb2hex or pass QColor directly
   ```python
   # Before
   pen = pg.mkPen(color=self.M_PRIMa)
   
   # After
   pen = pg.mkPen(color=self.rgb2hex(self.M_PRIMa))
   # or
   pen = pg.mkPen(color=QColor(*self.M_PRIMa))
   ```

3. **HTML font color tags** → Use hex format
   ```python
   # Before
   f"<font color={self.M_PRIMa}> Text"
   
   # After
   f"<font color=#{self.rgb2hex(self.M_PRIM)[1:]}> Text"
   ```

### Phase 2: Fix Dynamic Color Replacement (Stylesheet Rendering)

**Update `replaceColor()` method:**
- Change from returning `"rgba(...)"` strings
- Return valid hex colors: `"#2090C0"`
- Or use QSS-valid CSS: `"rgb(32, 144, 192)"`

```python
# Current
def replaceColor(self, line: str) -> str:
    rgba = colors[key][self.colorSet]
    rgba[3] = int(self.transparency * 255)
    color = f"rgba{tuple(rgba)}"  # ← Invalid CSS
    
# Proposed
def replaceColor(self, line: str) -> str:
    rgba = colors[key][self.colorSet]
    # Use hex format (valid in all CSS contexts)
    color = self.rgb2hex(rgba[:3])  # ← Valid hex color
```

### Phase 3: Add Helper Methods

Add convenient methods to Styles class for common conversions:

```python
@staticmethod
def rgb2hex(rgb: list[int]) -> str:
    """Convert RGB list to hex string: [32, 144, 192] → '#2090c0'"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

def rgb2qcolor(self, rgb: list[int]) -> QColor:
    """Convert RGB list to QColor object"""
    if len(rgb) == 4:
        return QColor(rgb[0], rgb[1], rgb[2], rgb[3])
    return QColor(rgb[0], rgb[1], rgb[2])

def rgba2css(self, rgb: list[int]) -> str:
    """Convert RGBA to CSS format: [32, 144, 192, 255] → 'rgba(32, 144, 192, 1.0)'"""
    alpha_norm = rgb[3] / 255.0 if len(rgb) > 3 else 1.0
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha_norm})"
```

### Phase 4: Update Affected Code (27 usages)

**tabAlmanac.py** (5 usages)
```python
# Before
self.ui.almanacCivil.setStyleSheet(f"background-color: {self.mainW.M_PRIM1as};")

# After
color = self.mainW.rgb2hex(self.mainW.M_PRIM1)
self.ui.almanacCivil.setStyleSheet(f"background-color: {color};")
```

**gPlotBase.py** (8 usages)
```python
# Before
self.brushGrid: QBrush = pg.mkBrush(color=self.M_PRIMa)

# After
self.brushGrid: QBrush = pg.mkBrush(color=QColor(*self.M_PRIMa))
# or
self.brushGrid: QBrush = pg.mkBrush(color=self.rgb2hex(self.M_PRIMa))
```

**image/imageW.py, hemisphereW.py, horizonDraw.py, hemisphereDraw.py** (12 usages)
- Replace `pg.mkPen/mkBrush(color=self.M_*a)` with `QColor(*self.M_*a)`
- Replace `<font color={self.M_*a}>` with hex colors

### Phase 5: Test Updates

Update test expectations:

**test_styles.py**
```python
# Before
assert val == "12345#2090C012345\n"

# After  
assert val == "12345#2090c012345\n"  # lowercase (matches rgb2hex output)
# or
expected_color = styles.rgb2hex(colors["M_PRIM"][0])
assert val == f"12345{expected_color}12345\n"
```

**test_qtMain.py**
```python
# Similar updates for dynamic color replacement
```

---

## Implementation Order

1. **Phase 1** - Remove `M_*s` and `M_*as` properties (1 day)
   - Modify `__getattr__` in styles.py
   - Fix compilation errors
   - Update tests

2. **Phase 2** - Add helper methods (0.5 day)
   - Implement rgb2hex, rgb2qcolor, rgba2css
   - Ensure backward compatibility

3. **Phase 3** - Update affected UI code (1-2 days)
   - tabAlmanac.py: 5 usages
   - gPlotBase.py: 8 usages  
   - Hemisphere/Image windows: 12 usages
   - Test each module independently

4. **Phase 4** - Fix stylesheet rendering (0.5 day)
   - Update replaceColor() logic
   - Verify stylesheet generation

5. **Phase 5** - Update tests (1 day)
   - Fix hardcoded color expectations
   - Verify 100% coverage maintained

**Total Effort:** ~4-5 days of development

---

## Benefits

✅ **Type Safety**
- Single, consistent return type (list[int]) from color properties
- Eliminates string parsing and format confusion
- PyLint/type checkers can validate more effectively

✅ **Reduced Complexity**
- Remove 4 property variants → single consistent API
- Fewer special cases in tests
- Easier to reason about color transformations

✅ **Better CSS Support**
- Hex colors work everywhere (CSS, HTML, Qt)
- Valid CSS format with proper alpha handling
- No more invalid rgba() strings

✅ **Maintainability**
- Central helper methods for conversions
- Easier to add new color formats (HSL, HSV, etc.)
- Clear responsibility separation

✅ **Test Coverage**
- Simpler assertions with consistent types
- Fewer hardcoded string expectations
- Easier to test color transformations

---

## Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking changes in public API | All Styles methods are internal; no public API broken |
| Color rendering issues | Test on all platforms (macOS, Windows, Linux) |
| Performance regression | Helper methods are trivial (string ops); no perf impact |
| Incomplete refactoring | Use grep to find all `.M_*` usages; systematic updates |

---

## Rollback Plan

If issues arise:
1. Keep current system in git history
2. Can revert specific usages if needed
3. Maintain backward compat layer temporarily if needed

---

## Success Criteria

- [ ] All string color properties removed
- [ ] 100% test coverage maintained
- [ ] All UI colors render correctly across platforms
- [ ] No performance degradation
- [ ] Code is easier to understand and modify
