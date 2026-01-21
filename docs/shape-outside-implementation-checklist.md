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

---

## Phase 1: Box Keywords Only

**Goal:** Implement `shape-outside` property with box keyword values only (`none`, `margin-box`, `border-box`, `padding-box`, `content-box`).

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

### 1.2 CSS Property Registration

- [ ] Add `shape_outside` to initial values
  - [ ] Edit `/weasyprint/css/properties.py`
  - [ ] Add entry: `'shape_outside': 'none'`
- [ ] Add property to computed values list (if needed)
  - [ ] Check `/weasyprint/css/computed_values.py`
- [ ] Verify property naming convention matches WeasyPrint style
  - [ ] Confirm underscore usage: `shape_outside` not `shape-outside`

### 1.3 CSS Validation

- [ ] Create validator for `shape-outside` property
  - [ ] Edit `/weasyprint/css/validation/properties.py`
  - [ ] Add `@property('shape-outside')` decorator
  - [ ] Implement validation function
  - [ ] Accept keywords: `none`, `margin-box`, `border-box`, `padding-box`, `content-box`
- [ ] Add to `__all__` exports if required
- [ ] Test CSS parsing with sample stylesheets
  - [ ] Test: `shape-outside: none`
  - [ ] Test: `shape-outside: margin-box`
  - [ ] Test: `shape-outside: border-box`
  - [ ] Test: `shape-outside: padding-box`
  - [ ] Test: `shape-outside: content-box`
  - [ ] Test: `shape-outside: invalid-value` (should be ignored)

### 1.4 Float Layout Integration

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
  - [ ] Existing float tests still pass

### 1.5 Testing - Phase 1

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
- [ ] Visual regression tests
  - [ ] Create reference PDFs for each box keyword
  - [ ] Compare against browser rendering (if possible)
- [ ] Run full test suite to ensure no regressions
  - [ ] `pytest tests/`

### 1.6 Documentation - Phase 1

- [ ] Add inline code comments explaining shape-outside logic
- [ ] Update docstrings for modified functions
- [ ] Note any browser compatibility considerations

### 1.7 Phase 1 Completion Checklist

- [ ] All Phase 1 tests passing
- [ ] Code reviewed (self or peer)
- [ ] No regressions in existing tests
- [ ] Commit changes with descriptive message
- [ ] Tag/note completion of Phase 1

---

## Phase 2: Shape Boundary Architecture

**Goal:** Create an extensible `ShapeBoundary` abstraction layer that encapsulates shape evaluation logic.

### 2.1 Preparation

- [ ] Review Phase 1 implementation
- [ ] Design class hierarchy for shape boundaries
  - [ ] `ShapeBoundary` (abstract base class)
  - [ ] `BoxBoundary` (replaces Phase 1 box logic)
  - [ ] Plan for future: `CircleBoundary`, `EllipseBoundary`, `PolygonBoundary`
- [ ] Decide on module location: `/weasyprint/layout/shapes.py`

### 2.2 Create Shape Boundary Module

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

### 2.3 Refactor Float Layout

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

### 2.4 Testing - Phase 2

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
- [ ] Run full test suite
  - [ ] `pytest tests/`

### 2.5 Phase 2 Completion Checklist

- [ ] All Phase 2 tests passing
- [ ] Phase 1 tests still passing (no regression)
- [ ] Architecture ready for shape function additions
- [ ] Code reviewed
- [ ] Commit changes with descriptive message
- [ ] Tag/note completion of Phase 2

---

## Phase 3: Basic Shapes (Circle, Ellipse, Polygon)

**Goal:** Implement `circle()`, `ellipse()`, and `polygon()` shape functions.

### 3.1 Preparation

- [ ] Review CSS Shapes Level 1 specification for shape functions
  - [ ] `circle()` syntax: `circle(radius? at position?)`
  - [ ] `ellipse()` syntax: `ellipse(rx ry? at position?)`
  - [ ] `polygon()` syntax: `polygon(fill-rule?, [x y]+)`
- [ ] Review position parsing in WeasyPrint
  - [ ] Locate existing position parsing code
  - [ ] Understand length/percentage resolution
- [ ] Review coordinate system and reference box rules

### 3.2 CSS Parsing - Circle

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
- [ ] Test circle parsing
  - [ ] Test: `circle()` - defaults
  - [ ] Test: `circle(50px)`
  - [ ] Test: `circle(50%)`
  - [ ] Test: `circle(closest-side)`
  - [ ] Test: `circle(farthest-side)`
  - [ ] Test: `circle(at top left)`
  - [ ] Test: `circle(100px at 25% 75%)`
  - [ ] Test: `circle(closest-side at center)`

### 3.3 CSS Parsing - Ellipse

- [ ] Extend `shape_outside` validator for `ellipse()` function
  - [ ] Detect function token with name `ellipse`
  - [ ] Parse optional rx, ry arguments
    - [ ] Accept length values for each radius
    - [ ] Accept percentage values
    - [ ] Accept `closest-side`, `farthest-side` keywords
    - [ ] Defaults: `closest-side closest-side`
  - [ ] Parse optional `at <position>` clause
  - [ ] Return tuple: `('ellipse', rx, ry, position)`
- [ ] Test ellipse parsing
  - [ ] Test: `ellipse()` - defaults
  - [ ] Test: `ellipse(50px 100px)`
  - [ ] Test: `ellipse(25% 50%)`
  - [ ] Test: `ellipse(closest-side farthest-side)`
  - [ ] Test: `ellipse(at bottom right)`
  - [ ] Test: `ellipse(100px 200px at 50% 50%)`

### 3.4 CSS Parsing - Polygon

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
- [ ] Test polygon parsing
  - [ ] Test: `polygon(0 0, 100% 0, 50% 100%)` - triangle
  - [ ] Test: `polygon(0 0, 100% 0, 100% 100%, 0 100%)` - rectangle
  - [ ] Test: `polygon(evenodd, 0 0, 100% 0, 50% 100%)`
  - [ ] Test: `polygon(nonzero, 50% 0, 100% 50%, 50% 100%, 0 50%)` - diamond
  - [ ] Test: `polygon(20px 20px, 80px 20px, 80px 80px)` - absolute units
  - [ ] Test: invalid polygon with <3 points rejected

### 3.5 Implement CircleBoundary

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

### 3.6 Implement EllipseBoundary

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

### 3.7 Implement PolygonBoundary

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

### 3.8 Update Shape Boundary Factory

- [ ] Modify `create_shape_boundary()` in `/weasyprint/layout/float.py`
  - [ ] Handle tuple values (shape functions)
  - [ ] Dispatch to appropriate boundary class
    - [ ] `('circle', ...)` -> `CircleBoundary`
    - [ ] `('ellipse', ...)` -> `EllipseBoundary`
    - [ ] `('polygon', ...)` -> `PolygonBoundary`
  - [ ] Pass reference box for parameter resolution
  - [ ] Fallback to `BoxBoundary(margin-box)` for unknown shapes

### 3.9 Testing - Phase 3

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
- [ ] Visual regression tests
  - [ ] Circle at various positions and sizes
  - [ ] Ellipse with different aspect ratios
  - [ ] Various polygon shapes
- [ ] Performance tests
  - [ ] Measure layout time with many polygon floats
  - [ ] Ensure acceptable performance

### 3.10 Phase 3 Completion Checklist

- [ ] All Phase 3 tests passing
- [ ] Phase 1 and 2 tests still passing
- [ ] circle(), ellipse(), polygon() all working
- [ ] Code reviewed
- [ ] Commit changes with descriptive message
- [ ] Tag/note completion of Phase 3

---

## Phase 4: Advanced Features

**Goal:** Implement `inset()`, `path()`, image-based shapes, and `shape-margin` property.

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

### 4.2 Implement Inset Shape

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
- [ ] Test inset shapes
  - [ ] Test: `inset(10px)`
  - [ ] Test: `inset(10px 20px)`
  - [ ] Test: `inset(10px 20px 30px 40px)`
  - [ ] Test: `inset(10px round 5px)`
  - [ ] Test: `inset(10% 20%)`

### 4.3 Implement Path Shape (Optional)

- [ ] Evaluate complexity vs. benefit of path() support
- [ ] Add CSS parsing for `path()` function
  - [ ] Syntax: `path(fill-rule?, 'd-string')`
  - [ ] Parse SVG path d-string
  - [ ] Reuse `/weasyprint/svg/path.py` parser if possible
- [ ] Add `PathBoundary` class
  - [ ] Convert path to series of line/curve segments
  - [ ] Implement scanline intersection with curves
  - [ ] Handle Bezier curve intersection math
- [ ] Test path shapes
  - [ ] Test simple path with lines only
  - [ ] Test path with curves
  - [ ] Test complex path shapes

### 4.4 Implement Image-Based Shapes

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
- [ ] Test image-based shapes
  - [ ] Test with simple PNG with transparency
  - [ ] Test different threshold values
  - [ ] Test image sizing/scaling
  - [ ] Test missing/invalid image fallback

### 4.5 Implement shape-margin Property

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
  - [ ] Polygon: offset edges outward by margin (complex!)
  - [ ] Inset: reduce inset by margin
- [ ] Test shape-margin
  - [ ] Test with various margin values
  - [ ] Test percentage margin
  - [ ] Test margin with each shape type

### 4.6 Reference Box Combinations

- [ ] Support shape function + box keyword combinations
  - [ ] Syntax: `circle(50%) border-box`
  - [ ] The box keyword specifies the reference box for the shape
  - [ ] Update CSS parsing to handle this
- [ ] Update factory to pass correct reference box
- [ ] Test combinations
  - [ ] Test: `circle(50%) content-box`
  - [ ] Test: `polygon(...) padding-box`

### 4.7 Testing - Phase 4

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
- [ ] Integration tests
  - [ ] Complex layouts with multiple advanced shapes
  - [ ] Shape-margin with various shapes
- [ ] Performance tests
  - [ ] Image-based shapes with large images
  - [ ] Complex paths
- [ ] Visual regression tests
  - [ ] All advanced shape types
  - [ ] Shape-margin effects

### 4.8 Edge Cases and Error Handling

- [ ] Handle invalid/missing images gracefully
  - [ ] Fallback to margin-box
- [ ] Handle malformed path strings
- [ ] Handle extreme values
  - [ ] Very large margins
  - [ ] Zero-size shapes
  - [ ] Negative values where not allowed
- [ ] Ensure thread safety for image processing
- [ ] Memory management for large images

### 4.9 Documentation - All Phases

- [ ] Update WeasyPrint documentation
  - [ ] Document supported shape-outside syntax
  - [ ] Document any limitations vs. CSS spec
  - [ ] Provide examples
- [ ] Add docstrings to all new classes and functions
- [ ] Update changelog/release notes
- [ ] Consider blog post or announcement

### 4.10 Phase 4 Completion Checklist

- [ ] All Phase 4 tests passing
- [ ] All previous phase tests passing
- [ ] All planned features implemented
- [ ] Code reviewed
- [ ] Documentation complete
- [ ] Commit changes with descriptive message
- [ ] Tag/note completion of Phase 4

---

## Final Release Checklist

- [ ] All 4 phases complete and tested
- [ ] Full test suite passing
- [ ] Performance acceptable
- [ ] Documentation complete
- [ ] Changelog updated
- [ ] Version number updated (if applicable)
- [ ] Create pull request
- [ ] Code review approved
- [ ] Merge to main branch
- [ ] Tag release
- [ ] Announce feature availability

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
- Start Date: ___________
- Completion Date: ___________
- Completed By: ___________

### Phase 2 Progress
- Start Date: ___________
- Completion Date: ___________
- Completed By: ___________

### Phase 3 Progress
- Start Date: ___________
- Completion Date: ___________
- Completed By: ___________

### Phase 4 Progress
- Start Date: ___________
- Completion Date: ___________
- Completed By: ___________

### Final Release
- Release Date: ___________
- Version: ___________
