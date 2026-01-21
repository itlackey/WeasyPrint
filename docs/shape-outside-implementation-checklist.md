# CSS Shape-Outside Implementation Checklist

**Project:** WeasyPrint CSS Shapes Level 1 Support
**Created:** January 2026
**Status:** In Progress

---

## Overview

This checklist tracks the implementation of CSS `shape-outside` property support in WeasyPrint. The implementation is divided into 4 phases, each building on the previous one.

### Phase Summary

| Phase | Description | Estimated Lines | Risk |
|-------|-------------|-----------------|------|
| 1 | Box Keywords Only | ~25 | Very Low |
| 2 | Shape Boundary Architecture | ~80 | Low |
| 3 | Basic Shapes (circle, ellipse, polygon) | ~150 | Low-Medium |
| 4 | Advanced Features (path, inset, image, shape-margin) | ~200+ | Medium |

### Development Process

Each phase follows a strict development and review cycle:

```
┌─────────────────────────────────────────────────────────────────┐
│                        PHASE N                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   CODING     │────▶│    TEST      │────▶│   REVIEW     │    │
│  │   AGENT      │     │   EXECUTION  │     │   AGENT      │    │
│  └──────────────┘     └──────────────┘     └──────┬───────┘    │
│         ▲                                         │             │
│         │              ┌──────────────┐           │             │
│         └──────────────│   ISSUES     │◀──────────┘             │
│           (if issues)  │   FOUND?     │                         │
│                        └──────┬───────┘                         │
│                               │ (no issues)                     │
│                               ▼                                 │
│                        ┌──────────────┐                         │
│                        │    STAGE     │                         │
│                        │    GATE      │                         │
│                        │   PASSED     │                         │
│                        └──────────────┘                         │
│                               │                                 │
└───────────────────────────────┼─────────────────────────────────┘
                                │
                                ▼
                         PROCEED TO PHASE N+1
```

**Stage Gate Requirements:**
- All tests for the phase must pass
- No regressions in previous phase tests
- Code review completed with no blocking issues
- Documentation updated
- Commit pushed with descriptive message

---

## Phase 1: Box Keywords Only

**Goal:** Implement `shape-outside` property with box keyword values only (`none`, `margin-box`, `border-box`, `padding-box`, `content-box`).

---

### 1.1 Preparation

- [ ] Review CSS Shapes Level 1 specification for box keywords
  - Spec URL: https://drafts.csswg.org/css-shapes/#shape-outside-property
- [ ] Review existing box model methods in `/weasyprint/formatting_structure/boxes.py`
  - [ ] Locate `margin_width()`, `margin_height()` methods
  - [ ] Locate `border_box_x()`, `border_box_y()` methods
  - [ ] Locate `padding_box_x()`, `padding_box_y()` methods
  - [ ] Locate `content_box_x()`, `content_box_y()` methods
- [ ] Review current float layout in `/weasyprint/layout/float.py`
  - [ ] Understand `float_layout()` function
  - [ ] Understand `avoid_collisions()` function
  - [ ] Identify where exclusion bounds are calculated

---

### 1.2 Development Tasks (Coding Agent)

#### 1.2.1 CSS Property Registration

- [ ] Add `shape_outside` to initial values
  - [ ] Edit `/weasyprint/css/properties.py`
  - [ ] Add entry: `'shape_outside': 'none'`
- [ ] Add property to computed values list (if needed)
  - [ ] Check `/weasyprint/css/computed_values.py`
- [ ] Verify property naming convention matches WeasyPrint style
  - [ ] Confirm underscore usage: `shape_outside` not `shape-outside`

#### 1.2.2 CSS Validation

- [ ] Create validator for `shape-outside` property
  - [ ] Edit `/weasyprint/css/validation/properties.py`
  - [ ] Add `@property('shape-outside')` decorator
  - [ ] Implement validation function
  - [ ] Accept keywords: `none`, `margin-box`, `border-box`, `padding-box`, `content-box`
- [ ] Add to `__all__` exports if required

#### 1.2.3 Float Layout Integration

- [ ] Modify `avoid_collisions()` in `/weasyprint/layout/float.py`
  - [ ] Add helper function `get_shape_box_bounds(box)`
  - [ ] Read `shape_outside` from box style
  - [ ] Return appropriate box dimensions based on keyword
  - [ ] Handle `none` as equivalent to `margin-box`
- [ ] Update exclusion calculation to use shape bounds
  - [ ] Replace direct margin box references with helper function
  - [ ] Ensure both left and right floats use shape bounds
- [ ] Verify backward compatibility
  - [ ] Default behavior (no shape-outside) unchanged

#### 1.2.4 Write Tests

- [ ] Create test file `/tests/test_shape_outside.py`
- [ ] Unit tests for CSS parsing
  - [ ] Test valid keyword values parse correctly
  - [ ] Test invalid values are rejected/ignored
  - [ ] Test inheritance behavior
  - [ ] Test specificity with multiple rules
- [ ] Unit tests for box bounds calculation
  - [ ] Test `margin-box` returns margin dimensions
  - [ ] Test `border-box` returns border dimensions
  - [ ] Test `padding-box` returns padding dimensions
  - [ ] Test `content-box` returns content dimensions
- [ ] Integration tests for float layout
  - [ ] Test left float with `shape-outside: content-box`
  - [ ] Test right float with `shape-outside: border-box`
  - [ ] Test text wrapping respects shape box

#### 1.2.5 Documentation

- [ ] Add inline code comments explaining shape-outside logic
- [ ] Update docstrings for modified functions
- [ ] Note any browser compatibility considerations

#### 1.2.6 Commit Development Work

- [ ] Stage all changes
- [ ] Commit with message: "Phase 1: Implement shape-outside box keywords"
- [ ] Push to feature branch

---

### 1.3 Test Execution Stage

**Run all tests to verify implementation:**

- [ ] Run Phase 1 specific tests
  ```bash
  pytest tests/test_shape_outside.py -v
  ```
- [ ] Run full test suite to check for regressions
  ```bash
  pytest tests/ -v
  ```
- [ ] Record test results:
  - Total tests: ___________
  - Passed: ___________
  - Failed: ___________
  - Skipped: ___________

**If tests fail:**
- [ ] Document failures in Review Findings section below
- [ ] Return to Coding Agent for fixes
- [ ] Re-run tests after fixes

---

### 1.4 Review Stage (Review Agent)

#### 1.4.1 Code Quality Review

- [ ] Review all modified files for code quality
  - [ ] `/weasyprint/css/properties.py`
  - [ ] `/weasyprint/css/validation/properties.py`
  - [ ] `/weasyprint/layout/float.py`
  - [ ] `/tests/test_shape_outside.py`
- [ ] Check coding style consistency with WeasyPrint codebase
- [ ] Verify no unnecessary changes outside scope
- [ ] Check for potential performance issues
- [ ] Verify error handling is appropriate

#### 1.4.2 Test Coverage Review

- [ ] Verify all new code paths have test coverage
- [ ] Check edge cases are tested:
  - [ ] Empty/none values
  - [ ] Invalid CSS values
  - [ ] Combination with other float properties
- [ ] Verify tests are meaningful (not just passing trivially)
- [ ] Check test naming follows conventions

#### 1.4.3 Specification Compliance Review

- [ ] Verify implementation matches CSS Shapes Level 1 spec for box keywords
- [ ] Document any intentional deviations from spec
- [ ] Verify backward compatibility is maintained

#### 1.4.4 Documentation Review

- [ ] Verify docstrings are complete and accurate
- [ ] Check inline comments explain non-obvious logic
- [ ] Verify any public API changes are documented

#### 1.4.5 Review Findings

| Issue # | Severity | File | Line | Description | Status |
|---------|----------|------|------|-------------|--------|
| | | | | | |
| | | | | | |
| | | | | | |

**Severity Levels:**
- **Blocker**: Must fix before proceeding
- **Major**: Should fix, may proceed with plan to address
- **Minor**: Nice to fix, does not block progress

---

### 1.5 Review Loop (Iterate Until Pass)

**If blocking issues found:**

- [ ] Coding Agent addresses all Blocker issues
- [ ] Coding Agent addresses Major issues (or documents deferral reason)
- [ ] Re-run Test Execution Stage (1.3)
- [ ] Re-run Review Stage (1.4)
- [ ] Repeat until no Blocker issues remain

**Review Loop Iterations:**

| Iteration | Date | Issues Found | Issues Fixed | Outcome |
|-----------|------|--------------|--------------|---------|
| 1 | | | | Pass / Fail |
| 2 | | | | Pass / Fail |
| 3 | | | | Pass / Fail |

---

### 1.6 Stage Gate: Phase 1 Completion

**All criteria must be checked to proceed to Phase 2:**

- [ ] All Phase 1 tests passing (0 failures)
- [ ] Full test suite passing (no regressions)
- [ ] Code review completed with no Blocker issues
- [ ] All Major issues addressed or documented for follow-up
- [ ] Documentation complete
- [ ] Changes committed and pushed
- [ ] Review Agent sign-off obtained

**Stage Gate Status:** ⬜ NOT PASSED / ✅ PASSED

**Sign-off:**
- Coding Agent: ___________ Date: ___________
- Review Agent: ___________ Date: ___________

---

## Phase 2: Shape Boundary Architecture

**Goal:** Create an extensible `ShapeBoundary` abstraction layer that encapsulates shape evaluation logic.

**Prerequisites:** Phase 1 Stage Gate PASSED ✅

---

### 2.1 Preparation

- [ ] Review Phase 1 implementation
- [ ] Design class hierarchy for shape boundaries
  - [ ] `ShapeBoundary` (abstract base class)
  - [ ] `BoxBoundary` (replaces Phase 1 box logic)
  - [ ] Plan for future: `CircleBoundary`, `EllipseBoundary`, `PolygonBoundary`
- [ ] Decide on module location: `/weasyprint/layout/shapes.py`
- [ ] Document design decisions in Notes section

---

### 2.2 Development Tasks (Coding Agent)

#### 2.2.1 Create Shape Boundary Module

- [ ] Create new file `/weasyprint/layout/shapes.py`
- [ ] Implement `ShapeBoundary` abstract base class
  - [ ] Define abstract method `get_bounds_at_y(y, box_x, box_width) -> tuple | None`
  - [ ] Define abstract method `get_vertical_extent() -> tuple`
  - [ ] Add docstrings explaining interface contract
- [ ] Implement `BoxBoundary` class
  - [ ] Constructor accepts box and box_type keyword
  - [ ] Implement `get_bounds_at_y()` - returns consistent horizontal bounds
  - [ ] Implement `get_vertical_extent()` - returns box vertical range
  - [ ] Handle all box types: margin, border, padding, content
- [ ] Add module to package exports
  - [ ] Update `/weasyprint/layout/__init__.py` if needed

#### 2.2.2 Refactor Float Layout

- [ ] Import shape boundary classes in `/weasyprint/layout/float.py`
- [ ] Create factory function `create_shape_boundary(box)`
  - [ ] Read `shape_outside` property from box style
  - [ ] Return appropriate `BoxBoundary` instance
  - [ ] Handle `none` keyword (return `BoxBoundary` with margin-box)
- [ ] Attach shape boundary to float boxes
  - [ ] In `float_layout()`, after positioning: `box.shape_boundary = create_shape_boundary(box)`
- [ ] Modify `avoid_collisions()` to use shape boundary
  - [ ] Call `shape.shape_boundary.get_bounds_at_y(current_y, ...)`
  - [ ] Handle `None` return (shape doesn't intersect at this Y)
  - [ ] Update left/right bound calculations

#### 2.2.3 Write Tests

- [ ] Unit tests for `ShapeBoundary` classes
  - [ ] Test `BoxBoundary` with each box type
  - [ ] Test `get_bounds_at_y()` returns correct values
  - [ ] Test `get_vertical_extent()` returns correct range
- [ ] Test factory function `create_shape_boundary()`
  - [ ] Test returns correct boundary type for each keyword
  - [ ] Test default behavior for `none`
- [ ] Integration tests
  - [ ] Verify Phase 1 tests still pass with new architecture
  - [ ] Test that refactoring doesn't change output

#### 2.2.4 Documentation

- [ ] Add module-level docstring to `shapes.py`
- [ ] Document class hierarchy and extension points
- [ ] Update any affected docstrings in `float.py`

#### 2.2.5 Commit Development Work

- [ ] Stage all changes
- [ ] Commit with message: "Phase 2: Implement ShapeBoundary architecture"
- [ ] Push to feature branch

---

### 2.3 Test Execution Stage

**Run all tests to verify implementation:**

- [ ] Run Phase 2 specific tests
  ```bash
  pytest tests/test_shape_outside.py -v
  ```
- [ ] Run full test suite to check for regressions
  ```bash
  pytest tests/ -v
  ```
- [ ] Verify Phase 1 functionality unchanged
  ```bash
  pytest tests/test_shape_outside.py -k "box_keyword" -v
  ```
- [ ] Record test results:
  - Total tests: ___________
  - Passed: ___________
  - Failed: ___________
  - Skipped: ___________

**If tests fail:**
- [ ] Document failures in Review Findings section below
- [ ] Return to Coding Agent for fixes
- [ ] Re-run tests after fixes

---

### 2.4 Review Stage (Review Agent)

#### 2.4.1 Architecture Review

- [ ] Review class hierarchy design
  - [ ] Is the abstraction appropriate?
  - [ ] Is it extensible for Phase 3 shapes?
  - [ ] Are the method signatures correct?
- [ ] Review factory function design
  - [ ] Is it easy to extend for new shapes?
  - [ ] Is error handling appropriate?
- [ ] Verify refactoring maintains behavior
  - [ ] Compare output before/after refactoring

#### 2.4.2 Code Quality Review

- [ ] Review all modified/new files
  - [ ] `/weasyprint/layout/shapes.py` (new)
  - [ ] `/weasyprint/layout/float.py`
  - [ ] `/weasyprint/layout/__init__.py`
  - [ ] `/tests/test_shape_outside.py`
- [ ] Check coding style consistency
- [ ] Verify no unnecessary changes outside scope
- [ ] Check for potential performance issues

#### 2.4.3 Test Coverage Review

- [ ] Verify all new classes/methods have test coverage
- [ ] Check architecture tests are meaningful
- [ ] Verify Phase 1 tests still provide coverage

#### 2.4.4 Documentation Review

- [ ] Verify module docstring explains purpose
- [ ] Check class docstrings are complete
- [ ] Verify extension points are documented

#### 2.4.5 Review Findings

| Issue # | Severity | File | Line | Description | Status |
|---------|----------|------|------|-------------|--------|
| | | | | | |
| | | | | | |

---

### 2.5 Review Loop (Iterate Until Pass)

**If blocking issues found:**

- [ ] Coding Agent addresses all Blocker issues
- [ ] Coding Agent addresses Major issues (or documents deferral)
- [ ] Re-run Test Execution Stage (2.3)
- [ ] Re-run Review Stage (2.4)
- [ ] Repeat until no Blocker issues remain

**Review Loop Iterations:**

| Iteration | Date | Issues Found | Issues Fixed | Outcome |
|-----------|------|--------------|--------------|---------|
| 1 | | | | Pass / Fail |
| 2 | | | | Pass / Fail |
| 3 | | | | Pass / Fail |

---

### 2.6 Stage Gate: Phase 2 Completion

**All criteria must be checked to proceed to Phase 3:**

- [ ] All Phase 2 tests passing (0 failures)
- [ ] All Phase 1 tests still passing (no regressions)
- [ ] Full test suite passing
- [ ] Architecture review approved
- [ ] Code review completed with no Blocker issues
- [ ] Documentation complete
- [ ] Changes committed and pushed
- [ ] Review Agent sign-off obtained

**Stage Gate Status:** ⬜ NOT PASSED / ✅ PASSED

**Sign-off:**
- Coding Agent: ___________ Date: ___________
- Review Agent: ___________ Date: ___________

---

## Phase 3: Basic Shapes (Circle, Ellipse, Polygon)

**Goal:** Implement `circle()`, `ellipse()`, and `polygon()` shape functions.

**Prerequisites:** Phase 2 Stage Gate PASSED ✅

---

### 3.1 Preparation

- [ ] Review CSS Shapes Level 1 specification for shape functions
  - [ ] `circle()` syntax: `circle(radius? at position?)`
  - [ ] `ellipse()` syntax: `ellipse(rx ry? at position?)`
  - [ ] `polygon()` syntax: `polygon(fill-rule?, [x y]+)`
- [ ] Review position parsing in WeasyPrint
  - [ ] Locate existing position parsing code
  - [ ] Understand length/percentage resolution
- [ ] Review coordinate system and reference box rules
- [ ] Review Phase 2 architecture for extension points

---

### 3.2 Development Tasks (Coding Agent)

#### 3.2.1 CSS Parsing - Circle

- [ ] Extend `shape_outside` validator for `circle()` function
  - [ ] Edit `/weasyprint/css/validation/properties.py`
  - [ ] Detect function token with name `circle`
  - [ ] Parse optional radius argument
    - [ ] Accept length values
    - [ ] Accept percentage values
    - [ ] Accept `closest-side` keyword (default)
    - [ ] Accept `farthest-side` keyword
  - [ ] Parse optional `at <position>` clause
    - [ ] Default position: `50% 50%` (center)
    - [ ] Accept standard position keywords and values
  - [ ] Return tuple: `('circle', radius, position)`

#### 3.2.2 CSS Parsing - Ellipse

- [ ] Extend `shape_outside` validator for `ellipse()` function
  - [ ] Detect function token with name `ellipse`
  - [ ] Parse optional rx, ry arguments
    - [ ] Accept length values for each radius
    - [ ] Accept percentage values
    - [ ] Accept `closest-side`, `farthest-side` keywords
    - [ ] Defaults: `closest-side closest-side`
  - [ ] Parse optional `at <position>` clause
  - [ ] Return tuple: `('ellipse', rx, ry, position)`

#### 3.2.3 CSS Parsing - Polygon

- [ ] Extend `shape_outside` validator for `polygon()` function
  - [ ] Detect function token with name `polygon`
  - [ ] Parse optional fill-rule
    - [ ] Accept `nonzero` (default)
    - [ ] Accept `evenodd`
  - [ ] Parse coordinate pairs
    - [ ] Split on commas
    - [ ] Each pair: `<length-percentage> <length-percentage>`
    - [ ] Require at least 3 points
  - [ ] Return tuple: `('polygon', fill_rule, points_tuple)`

#### 3.2.4 Implement CircleBoundary

- [ ] Add `CircleBoundary` class to `/weasyprint/layout/shapes.py`
  - [ ] Constructor: `__init__(self, cx, cy, radius)`
  - [ ] Store center coordinates and radius (resolved to absolute values)
  - [ ] Implement `get_bounds_at_y(y, box_x, box_width)`
    - [ ] Calculate `dy = y - cy`
    - [ ] Return `None` if `|dy| > radius`
    - [ ] Calculate `dx = sqrt(radius² - dy²)`
    - [ ] Return `(cx - dx, cx + dx)`
  - [ ] Implement `get_vertical_extent()`
    - [ ] Return `(cy - radius, cy + radius)`
- [ ] Add helper function `resolve_circle_params(shape_value, reference_box)`
  - [ ] Resolve position to absolute cx, cy
  - [ ] Resolve radius keyword or value to absolute radius
    - [ ] `closest-side`: min distance from center to any edge
    - [ ] `farthest-side`: max distance from center to any edge
    - [ ] Percentage: resolve against `sqrt(width² + height²) / sqrt(2)`

#### 3.2.5 Implement EllipseBoundary

- [ ] Add `EllipseBoundary` class to `/weasyprint/layout/shapes.py`
  - [ ] Constructor: `__init__(self, cx, cy, rx, ry)`
  - [ ] Store center and both radii
  - [ ] Implement `get_bounds_at_y(y, box_x, box_width)`
    - [ ] Calculate `dy = y - cy`
    - [ ] Return `None` if `|dy| > ry`
    - [ ] Calculate ratio: `1 - (dy² / ry²)`
    - [ ] Calculate `dx = rx * sqrt(ratio)`
    - [ ] Return `(cx - dx, cx + dx)`
  - [ ] Implement `get_vertical_extent()`
    - [ ] Return `(cy - ry, cy + ry)`
- [ ] Add helper function `resolve_ellipse_params(shape_value, reference_box)`
  - [ ] Resolve position to absolute cx, cy
  - [ ] Resolve rx (percentage against width, keywords same as circle)
  - [ ] Resolve ry (percentage against height)

#### 3.2.6 Implement PolygonBoundary

- [ ] Add `PolygonBoundary` class to `/weasyprint/layout/shapes.py`
  - [ ] Constructor: `__init__(self, points, fill_rule='nonzero')`
  - [ ] Store list of absolute (x, y) coordinate tuples
  - [ ] Precompute vertical extent in constructor
  - [ ] Implement `get_bounds_at_y(y, box_x, box_width)`
    - [ ] Return `None` if y outside vertical extent
    - [ ] Implement scanline intersection algorithm
      - [ ] Iterate through polygon edges
      - [ ] Find intersections with horizontal line at y
      - [ ] Sort intersections
      - [ ] Return `(min(intersections), max(intersections))`
    - [ ] Handle edge cases (horizontal edges, vertex hits)
  - [ ] Implement `get_vertical_extent()`
    - [ ] Return precomputed `(min_y, max_y)`
- [ ] Add helper function `resolve_polygon_params(shape_value, reference_box)`
  - [ ] Extract fill_rule and points from shape_value
  - [ ] Resolve each point's x percentage against box width
  - [ ] Resolve each point's y percentage against box height
  - [ ] Add box origin offset to get absolute coordinates

#### 3.2.7 Update Shape Boundary Factory

- [ ] Modify `create_shape_boundary()` in `/weasyprint/layout/float.py`
  - [ ] Handle tuple values (shape functions)
  - [ ] Dispatch to appropriate boundary class
    - [ ] `('circle', ...)` -> `CircleBoundary`
    - [ ] `('ellipse', ...)` -> `EllipseBoundary`
    - [ ] `('polygon', ...)` -> `PolygonBoundary`
  - [ ] Pass reference box for parameter resolution
  - [ ] Fallback to `BoxBoundary(margin-box)` for unknown shapes

#### 3.2.8 Write Tests

- [ ] Unit tests for CSS parsing
  - [ ] Test `circle()` with various arguments
  - [ ] Test `ellipse()` with various arguments
  - [ ] Test `polygon()` with various arguments
  - [ ] Test invalid syntax handling
- [ ] Unit tests for `CircleBoundary`
  - [ ] Test bounds at center (y = cy)
  - [ ] Test bounds at edge (y = cy ± radius)
  - [ ] Test bounds outside circle returns None
  - [ ] Test bounds at intermediate y values
  - [ ] Test vertical extent
- [ ] Unit tests for `EllipseBoundary`
  - [ ] Test bounds at center
  - [ ] Test bounds at vertical extremes
  - [ ] Test bounds outside ellipse returns None
  - [ ] Test asymmetric radii (rx ≠ ry)
- [ ] Unit tests for `PolygonBoundary`
  - [ ] Test simple triangle
  - [ ] Test rectangle
  - [ ] Test convex polygon (diamond, hexagon)
  - [ ] Test concave polygon (star, L-shape)
  - [ ] Test bounds outside polygon
  - [ ] Test edge cases (vertex intersections)
- [ ] Unit tests for parameter resolution
  - [ ] Test percentage to absolute conversion
  - [ ] Test `closest-side` radius calculation
  - [ ] Test `farthest-side` radius calculation
  - [ ] Test position keyword resolution
- [ ] Integration tests for float layout
  - [ ] Test circle float with text wrapping
  - [ ] Test ellipse float with text wrapping
  - [ ] Test polygon float with text wrapping
  - [ ] Test combination of different shapes

#### 3.2.9 Documentation

- [ ] Document each new boundary class
- [ ] Document CSS parsing for each shape function
- [ ] Add usage examples in docstrings

#### 3.2.10 Commit Development Work

- [ ] Stage all changes
- [ ] Commit with message: "Phase 3: Implement circle, ellipse, polygon shapes"
- [ ] Push to feature branch

---

### 3.3 Test Execution Stage

**Run all tests to verify implementation:**

- [ ] Run Phase 3 specific tests
  ```bash
  pytest tests/test_shape_outside.py -v
  ```
- [ ] Run geometry unit tests
  ```bash
  pytest tests/test_shape_outside.py -k "boundary" -v
  ```
- [ ] Run full test suite to check for regressions
  ```bash
  pytest tests/ -v
  ```
- [ ] Run performance benchmark (if available)
  ```bash
  pytest tests/test_shape_outside.py -k "performance" -v
  ```
- [ ] Record test results:
  - Total tests: ___________
  - Passed: ___________
  - Failed: ___________
  - Skipped: ___________

**If tests fail:**
- [ ] Document failures in Review Findings section below
- [ ] Return to Coding Agent for fixes
- [ ] Re-run tests after fixes

---

### 3.4 Review Stage (Review Agent)

#### 3.4.1 Geometry Algorithm Review

- [ ] Review `CircleBoundary` math
  - [ ] Verify circle intersection formula is correct
  - [ ] Check edge cases (tangent lines, etc.)
- [ ] Review `EllipseBoundary` math
  - [ ] Verify ellipse intersection formula is correct
  - [ ] Check asymmetric radius handling
- [ ] Review `PolygonBoundary` scanline algorithm
  - [ ] Verify intersection calculation is correct
  - [ ] Check handling of horizontal edges
  - [ ] Check handling of vertex intersections
  - [ ] Verify winding rule handling (if applicable)

#### 3.4.2 CSS Parsing Review

- [ ] Verify circle() parsing matches CSS spec
- [ ] Verify ellipse() parsing matches CSS spec
- [ ] Verify polygon() parsing matches CSS spec
- [ ] Check error handling for malformed input

#### 3.4.3 Code Quality Review

- [ ] Review all modified/new files
- [ ] Check coding style consistency
- [ ] Verify no unnecessary complexity
- [ ] Check for potential performance issues
  - [ ] Polygon scanline efficiency
  - [ ] Parameter resolution caching

#### 3.4.4 Test Coverage Review

- [ ] Verify all boundary classes have comprehensive tests
- [ ] Check edge cases are covered
- [ ] Verify integration tests are meaningful
- [ ] Check for missing test scenarios

#### 3.4.5 Documentation Review

- [ ] Verify all new classes are documented
- [ ] Check algorithm explanations are clear
- [ ] Verify CSS syntax is documented

#### 3.4.6 Review Findings

| Issue # | Severity | File | Line | Description | Status |
|---------|----------|------|------|-------------|--------|
| | | | | | |
| | | | | | |

---

### 3.5 Review Loop (Iterate Until Pass)

**If blocking issues found:**

- [ ] Coding Agent addresses all Blocker issues
- [ ] Coding Agent addresses Major issues (or documents deferral)
- [ ] Re-run Test Execution Stage (3.3)
- [ ] Re-run Review Stage (3.4)
- [ ] Repeat until no Blocker issues remain

**Review Loop Iterations:**

| Iteration | Date | Issues Found | Issues Fixed | Outcome |
|-----------|------|--------------|--------------|---------|
| 1 | | | | Pass / Fail |
| 2 | | | | Pass / Fail |
| 3 | | | | Pass / Fail |

---

### 3.6 Stage Gate: Phase 3 Completion

**All criteria must be checked to proceed to Phase 4:**

- [ ] All Phase 3 tests passing (0 failures)
- [ ] All Phase 1 and Phase 2 tests still passing (no regressions)
- [ ] Full test suite passing
- [ ] Geometry algorithms verified correct
- [ ] CSS parsing matches specification
- [ ] Code review completed with no Blocker issues
- [ ] Documentation complete
- [ ] Changes committed and pushed
- [ ] Review Agent sign-off obtained

**Stage Gate Status:** ⬜ NOT PASSED / ✅ PASSED

**Sign-off:**
- Coding Agent: ___________ Date: ___________
- Review Agent: ___________ Date: ___________

---

## Phase 4: Advanced Features

**Goal:** Implement `inset()`, `path()`, image-based shapes, and `shape-margin` property.

**Prerequisites:** Phase 3 Stage Gate PASSED ✅

---

### 4.1 Preparation

- [ ] Review remaining CSS Shapes Level 1 features
  - [ ] `inset()` function syntax
  - [ ] `path()` function syntax (if in scope)
  - [ ] `shape-outside: url(image)` behavior
  - [ ] `shape-image-threshold` property
  - [ ] `shape-margin` property
- [ ] Prioritize features based on user demand
- [ ] Review SVG path parsing in `/weasyprint/svg/path.py`
- [ ] Review image alpha extraction in `/weasyprint/images.py`
- [ ] Make go/no-go decision on `path()` implementation

---

### 4.2 Development Tasks (Coding Agent)

#### 4.2.1 Implement Inset Shape

- [ ] Add CSS parsing for `inset()` function
  - [ ] Syntax: `inset(offset{1,4} round border-radius?)`
  - [ ] Parse 1-4 offset values (like margin/padding shorthand)
  - [ ] Parse optional `round` keyword and border-radius values
  - [ ] Return tuple: `('inset', offsets, border_radius)`
- [ ] Add `InsetBoundary` class
  - [ ] Constructor: `__init__(self, top, right, bottom, left, border_radius, reference_box)`
  - [ ] Calculate inset rectangle bounds
  - [ ] Handle rounded corners (adjust bounds at corners)
  - [ ] Implement `get_bounds_at_y()`
    - [ ] For non-rounded: return constant left/right
    - [ ] For rounded: calculate curve intersection at corners
  - [ ] Implement `get_vertical_extent()`

#### 4.2.2 Implement Path Shape (If Decided Yes)

- [ ] Decision: Implement path()? ⬜ YES / ⬜ NO / ⬜ DEFER
- [ ] Add CSS parsing for `path()` function
  - [ ] Syntax: `path(fill-rule?, 'd-string')`
  - [ ] Parse SVG path d-string
  - [ ] Reuse `/weasyprint/svg/path.py` parser if possible
- [ ] Add `PathBoundary` class
  - [ ] Convert path to series of line/curve segments
  - [ ] Implement scanline intersection with curves
  - [ ] Handle Bezier curve intersection math

#### 4.2.3 Implement Image-Based Shapes

- [ ] Add CSS parsing for `url()` in shape-outside
  - [ ] Detect url() function token
  - [ ] Store image URL reference
  - [ ] Return tuple: `('image', url, box_keyword)`
  - [ ] Handle combined: `url(image.png) border-box`
- [ ] Add `shape-image-threshold` property
  - [ ] Edit `/weasyprint/css/properties.py` - add initial value (0.0)
  - [ ] Edit validation - accept number 0.0-1.0
- [ ] Add `ImageBoundary` class
  - [ ] Constructor: `__init__(self, image, threshold, reference_box)`
  - [ ] Load image and extract alpha channel
  - [ ] Implement `get_bounds_at_y()`
    - [ ] Map y coordinate to image row
    - [ ] Scan alpha values to find left/right bounds
    - [ ] Use threshold to determine "inside" shape
  - [ ] Cache scanline results for performance
  - [ ] Handle image scaling to reference box

#### 4.2.4 Implement shape-margin Property

- [ ] Add CSS property `shape-margin`
  - [ ] Edit `/weasyprint/css/properties.py` - add initial value (0)
  - [ ] Edit validation - accept length or percentage
- [ ] Modify shape boundary classes to support margin
  - [ ] Option A: Wrapper class `MarginedBoundary(inner_boundary, margin)`
  - [ ] Option B: Add margin parameter to each boundary class
- [ ] Implement margin expansion for each shape type
  - [ ] Box: expand by margin on all sides
  - [ ] Circle: increase radius by margin
  - [ ] Ellipse: increase both radii by margin
  - [ ] Polygon: offset edges outward by margin
  - [ ] Inset: reduce inset by margin

#### 4.2.5 Reference Box Combinations

- [ ] Support shape function + box keyword combinations
  - [ ] Syntax: `circle(50%) border-box`
  - [ ] The box keyword specifies the reference box for the shape
  - [ ] Update CSS parsing to handle this
- [ ] Update factory to pass correct reference box

#### 4.2.6 Edge Cases and Error Handling

- [ ] Handle invalid/missing images gracefully
  - [ ] Fallback to margin-box
- [ ] Handle malformed path strings
- [ ] Handle extreme values
  - [ ] Very large margins
  - [ ] Zero-size shapes
  - [ ] Negative values where not allowed
- [ ] Ensure thread safety for image processing
- [ ] Memory management for large images

#### 4.2.7 Write Tests

- [ ] Unit tests for InsetBoundary
  - [ ] Test various offset combinations
  - [ ] Test rounded corners
- [ ] Unit tests for PathBoundary (if implemented)
  - [ ] Test line segments
  - [ ] Test curves
- [ ] Unit tests for ImageBoundary
  - [ ] Test alpha extraction
  - [ ] Test threshold behavior
  - [ ] Test bounds calculation
- [ ] Unit tests for shape-margin
  - [ ] Test margin expansion for each shape type
- [ ] Unit tests for reference box combinations
- [ ] Integration tests
  - [ ] Complex layouts with multiple advanced shapes
  - [ ] Shape-margin with various shapes
- [ ] Performance tests
  - [ ] Image-based shapes with large images
  - [ ] Complex paths
- [ ] Edge case tests
  - [ ] Missing images
  - [ ] Malformed paths
  - [ ] Extreme values

#### 4.2.8 Documentation

- [ ] Document all new features
- [ ] Add usage examples
- [ ] Document limitations vs. CSS spec
- [ ] Update changelog/release notes

#### 4.2.9 Commit Development Work

- [ ] Stage all changes
- [ ] Commit with message: "Phase 4: Implement advanced shape-outside features"
- [ ] Push to feature branch

---

### 4.3 Test Execution Stage

**Run all tests to verify implementation:**

- [ ] Run Phase 4 specific tests
  ```bash
  pytest tests/test_shape_outside.py -v
  ```
- [ ] Run all shape-outside tests
  ```bash
  pytest tests/test_shape_outside.py -v
  ```
- [ ] Run full test suite to check for regressions
  ```bash
  pytest tests/ -v
  ```
- [ ] Run performance benchmarks
  ```bash
  pytest tests/test_shape_outside.py -k "performance" -v
  ```
- [ ] Record test results:
  - Total tests: ___________
  - Passed: ___________
  - Failed: ___________
  - Skipped: ___________

**If tests fail:**
- [ ] Document failures in Review Findings section below
- [ ] Return to Coding Agent for fixes
- [ ] Re-run tests after fixes

---

### 4.4 Review Stage (Review Agent)

#### 4.4.1 Feature Completeness Review

- [ ] Verify inset() implementation complete
- [ ] Verify path() implementation complete (if decided yes)
- [ ] Verify image-based shapes implementation complete
- [ ] Verify shape-margin implementation complete
- [ ] Verify reference box combinations work
- [ ] Document any deferred features

#### 4.4.2 Algorithm Review

- [ ] Review InsetBoundary math (especially rounded corners)
- [ ] Review PathBoundary curve intersection (if implemented)
- [ ] Review ImageBoundary alpha scanning
- [ ] Review shape-margin expansion for each shape type

#### 4.4.3 Performance Review

- [ ] Review image processing performance
- [ ] Check for memory leaks with large images
- [ ] Verify caching is effective
- [ ] Check path() performance (if implemented)

#### 4.4.4 Error Handling Review

- [ ] Verify graceful degradation for missing images
- [ ] Verify malformed input handling
- [ ] Check edge case behavior

#### 4.4.5 Code Quality Review

- [ ] Review all modified/new files
- [ ] Check coding style consistency
- [ ] Verify no unnecessary complexity
- [ ] Check for security issues (image loading)

#### 4.4.6 Test Coverage Review

- [ ] Verify all new features have comprehensive tests
- [ ] Check edge cases are covered
- [ ] Verify performance tests exist
- [ ] Check for missing test scenarios

#### 4.4.7 Documentation Review

- [ ] Verify all new features are documented
- [ ] Check usage examples are clear
- [ ] Verify limitations are documented
- [ ] Check changelog is updated

#### 4.4.8 Review Findings

| Issue # | Severity | File | Line | Description | Status |
|---------|----------|------|------|-------------|--------|
| | | | | | |
| | | | | | |

---

### 4.5 Review Loop (Iterate Until Pass)

**If blocking issues found:**

- [ ] Coding Agent addresses all Blocker issues
- [ ] Coding Agent addresses Major issues (or documents deferral)
- [ ] Re-run Test Execution Stage (4.3)
- [ ] Re-run Review Stage (4.4)
- [ ] Repeat until no Blocker issues remain

**Review Loop Iterations:**

| Iteration | Date | Issues Found | Issues Fixed | Outcome |
|-----------|------|--------------|--------------|---------|
| 1 | | | | Pass / Fail |
| 2 | | | | Pass / Fail |
| 3 | | | | Pass / Fail |

---

### 4.6 Stage Gate: Phase 4 Completion

**All criteria must be checked to proceed to Final Release:**

- [ ] All Phase 4 tests passing (0 failures)
- [ ] All Phase 1, 2, and 3 tests still passing (no regressions)
- [ ] Full test suite passing
- [ ] All planned features implemented (or documented as deferred)
- [ ] Performance acceptable
- [ ] Code review completed with no Blocker issues
- [ ] Documentation complete
- [ ] Changes committed and pushed
- [ ] Review Agent sign-off obtained

**Stage Gate Status:** ⬜ NOT PASSED / ✅ PASSED

**Sign-off:**
- Coding Agent: ___________ Date: ___________
- Review Agent: ___________ Date: ___________

---

## Final Release Stage

**Prerequisites:** All Phase Stage Gates PASSED ✅

---

### 5.1 Final Integration Testing

- [ ] Run complete test suite
  ```bash
  pytest tests/ -v --tb=short
  ```
- [ ] Run shape-outside specific tests
  ```bash
  pytest tests/test_shape_outside.py -v
  ```
- [ ] Manual testing with sample documents
  - [ ] Test all shape types
  - [ ] Test complex layouts
  - [ ] Test edge cases
- [ ] Cross-reference with browser rendering (where possible)
- [ ] Record final test results:
  - Total tests: ___________
  - Passed: ___________
  - Failed: ___________
  - Coverage: ___________%

---

### 5.2 Final Documentation Review

- [ ] Review all docstrings are complete
- [ ] Review changelog entry
- [ ] Review user-facing documentation
- [ ] Create/update feature documentation
- [ ] Document known limitations
- [ ] Document browser compatibility notes

---

### 5.3 Final Code Review

- [ ] Review entire feature branch diff
- [ ] Check for any lingering TODOs
- [ ] Verify no debug code remains
- [ ] Check for any security concerns
- [ ] Verify coding standards compliance

---

### 5.4 Release Preparation

- [ ] Squash/organize commits (if desired)
- [ ] Write comprehensive PR description
- [ ] Link to related issues
- [ ] Prepare release notes

---

### 5.5 Release Checklist

- [ ] Create pull request
- [ ] PR review approved
- [ ] All CI checks passing
- [ ] Merge to main branch
- [ ] Tag release (if applicable)
- [ ] Update documentation site (if applicable)
- [ ] Announce feature availability

---

### 5.6 Final Sign-off

**All criteria must be checked for release:**

- [ ] All tests passing
- [ ] All documentation complete
- [ ] All reviews approved
- [ ] PR merged successfully

**Release Status:** ⬜ NOT RELEASED / ✅ RELEASED

**Final Sign-off:**
- Coding Agent: ___________ Date: ___________
- Review Agent: ___________ Date: ___________
- Project Lead: ___________ Date: ___________

---

## Notes and Decisions Log

Use this section to track important decisions, open questions, and notes during implementation.

### Open Questions

- [ ] Should we support `path()` in Phase 4, or defer to a future release?
- [ ] What should the default `shape-image-threshold` be? (spec says 0.0)
- [ ] How should we handle floats with shapes that extend outside the float box?
- [ ] Performance target: how many shaped floats per page before degradation?

### Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| | | |

### Known Limitations

- (Document any spec features intentionally not implemented)
- (Document any browser differences)

### Resources

- [CSS Shapes Level 1 Specification](https://drafts.csswg.org/css-shapes/)
- [MDN: shape-outside](https://developer.mozilla.org/en-US/docs/Web/CSS/shape-outside)
- [WeasyPrint Implementation Analysis](./shape-outside-implementation-analysis.md)

---

## Progress Tracking

### Phase 1 Progress
- Start Date: January 21, 2026
- Stage Gate Passed: January 21, 2026 ✅
- Completed By: Claude Code (Coding Agent + Review Agent)

### Phase 2 Progress
- Start Date: January 21, 2026
- Stage Gate Passed: January 21, 2026 ✅
- Completed By: Claude Code (Coding Agent + Review Agent)

### Phase 3 Progress
- Start Date: January 21, 2026
- Stage Gate Passed: January 21, 2026 ✅
- Completed By: Claude Code (Coding Agent + Review Agent)

### Phase 4 Progress
- Start Date: January 21, 2026
- Stage Gate Passed: January 21, 2026 ✅
- Completed By: Claude Code (Coding Agent + Review Agent)

### Final Release
- Validation Date: January 21, 2026 ✅
- Total Tests: 117 shape-outside tests, 1001 layout tests passing
- Branch: claude/analyze-shape-outside-support-Hf6eY
