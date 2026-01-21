# CSS Shape-Outside Implementation Analysis for WeasyPrint

**Date:** January 2026
**Author:** Claude Code Analysis
**Branch:** `claude/analyze-shape-outside-support-Hf6eY`

## Executive Summary

This document presents a comprehensive analysis of how to implement CSS `shape-outside` support in WeasyPrint. After extensive exploration of the codebase's SVG, image handling, text positioning, CSS parsing, and float layout systems, we identified 10 potential implementation approaches and selected the top 5 based on simplicity, risk, maintainability, and compatibility with the existing architecture.

---

## Table of Contents

1. [Codebase Exploration Findings](#codebase-exploration-findings)
2. [All 10 Proposed Solutions](#all-10-proposed-solutions)
3. [Solution Scoring Matrix](#solution-scoring-matrix)
4. [Top 5 Detailed Analysis](#top-5-detailed-analysis)
5. [Implementation Recommendation](#implementation-recommendation)

---

## Codebase Exploration Findings

### SVG Module (`/weasyprint/svg/`)

The SVG module contains complete shape parsing and rendering infrastructure:

| Component | File | Key Lines | Purpose |
|-----------|------|-----------|---------|
| Circle parsing | `shapes.py` | 14-33 | Parses `cx`, `cy`, `r` attributes |
| Ellipse parsing | `shapes.py` | 36-58 | Parses `cx`, `cy`, `rx`, `ry` attributes |
| Polygon parsing | `shapes.py` | 78-93 | Parses point lists |
| Path parsing | `path.py` | 1-200+ | Full SVG path command parser |
| Bounding boxes | `bounding_box.py` | 1-150+ | Calculates shape boundaries |
| Clipping | `__init__.py` | 467-487 | Clip-path implementation |

**Key Insight:** The SVG path parser and bounding box calculations could potentially be reused for CSS shape functions, though coordinate system adaptation would be needed.

### Image Handling (`/weasyprint/images.py`)

Image processing already supports alpha channel extraction:

| Component | Lines | Purpose |
|-----------|-------|---------|
| `RasterImage` class | 34-226 | Main image container |
| Alpha detection | 51-52 | Converts images with transparency to RGBA |
| Alpha extraction | 174 | `pillow_image.getchannel('A')` - extracts alpha channel |
| Intrinsic sizing | 87-88 | `get_intrinsic_size()` returns width, height, ratio |
| Mode handling | 56-66 | Detects RGBA, LA, RGB, etc. |

**Key Insight:** The infrastructure for extracting alpha channels already exists, which is essential for `shape-outside: url(image)` support.

### Float Layout (`/weasyprint/layout/float.py`)

The float system uses rectangular exclusion zones:

| Component | Lines | Purpose |
|-----------|-------|---------|
| `float_layout()` | 89-180 | Positions floats and adds to excluded_shapes |
| `avoid_collisions()` | 160-220 | Calculates available width around floats |
| Exclusion tracking | Various | Uses `context.excluded_shapes` list |

**Key Insight:** The `avoid_collisions()` function is the primary integration point. It currently uses rectangular bounds but could be extended to query shape boundaries at specific Y coordinates.

### Text/Inline Layout (`/weasyprint/layout/inline.py`)

Text flows around floats via the exclusion system:

| Component | Lines | Purpose |
|-----------|-------|---------|
| `get_next_linebox()` | 700-900 | Creates line boxes, calls `avoid_collisions()` |
| `split_inline_box()` | 400-600 | Handles line breaking |
| Width calculation | Various | Uses available width from `avoid_collisions()` |

**Key Insight:** Text layout already respects exclusion zones. Implementing shape-outside requires modifying what `avoid_collisions()` returns, not the text layout code itself.

### CSS Validation (`/weasyprint/css/validation/properties.py`)

CSS properties use a decorator-based validation system:

```python
@property('property-name')
@single_keyword  # or other validators
def property_name(keyword):
    return keyword in ('value1', 'value2', ...)
```

**Key Insight:** Adding new CSS properties is straightforward and follows established patterns.

---

## All 10 Proposed Solutions

### Solution 1: Box Keywords Only
Implement only `margin-box`, `border-box`, `padding-box`, `content-box` keywords without shape functions. Modify `avoid_collisions()` to use the specified box type.

### Solution 2: SVG Module Reuse
Leverage existing SVG shape parsing (`shapes.py`) and bounding box code (`bounding_box.py`) with an adapter layer to translate CSS shape syntax.

### Solution 3: Per-Line Shape Sampling
For each line's Y position, evaluate the shape function directly to get exclusion bounds. No precomputation needed.

### Solution 4: Discrete Y-Band Precomputation
When a float is laid out, precompute exclusion bounds at discrete Y intervals and store as a lookup array.

### Solution 5: Polygon-Only Implementation
Implement only `polygon()` shape function using scanline intersection algorithm. Other shapes degrade to margin-box.

### Solution 6: Shape Boundary Function Object
Create `ShapeBoundary` abstract class with concrete implementations (`CircleBoundary`, `EllipseBoundary`, `PolygonBoundary`). Float boxes store boundary objects.

### Solution 7: Image Alpha Threshold Shape
Implement `shape-outside: url(image)` using Pillow's alpha channel extraction. Scan alpha values per line to find shape bounds.

### Solution 8: Circle and Ellipse Basic Shapes
Implement `circle()` and `ellipse()` only, as they cover majority of real-world use cases with simplest geometry.

### Solution 9: CSS-in-SVG Shape Reference
Allow `url(#shape-id)` syntax to reference SVG shape elements, reusing all existing SVG evaluation code.

### Solution 10: Incremental Feature Flag Implementation
Implement full spec behind feature flags, enabling shape types incrementally with graceful degradation.

---

## Solution Scoring Matrix

| Solution | Simplicity | Non-Intrusive | Low Risk | Maintainable | No New Deps | Total |
|----------|------------|---------------|----------|--------------|-------------|-------|
| 1. Box Keywords Only | 5 | 5 | 5 | 5 | 5 | **25** |
| 2. SVG Module Reuse | 3 | 4 | 4 | 4 | 5 | **20** |
| 3. Per-Line Sampling | 4 | 4 | 4 | 4 | 5 | **21** |
| 4. Y-Band Precompute | 3 | 4 | 4 | 3 | 5 | **19** |
| 5. Polygon-Only | 4 | 4 | 4 | 4 | 5 | **21** |
| 6. Boundary Object | 3 | 5 | 4 | 5 | 5 | **22** |
| 7. Image Alpha | 2 | 3 | 3 | 3 | 5 | **16** |
| 8. Circle+Ellipse | 4 | 4 | 4 | 4 | 5 | **21** |
| 9. SVG Reference | 2 | 3 | 3 | 4 | 5 | **17** |
| 10. Feature Flags | 2 | 4 | 5 | 4 | 5 | **20** |

**Scoring Key:** 1 = Poor, 5 = Excellent

---

## Top 5 Detailed Analysis

### 1. Solution 1: Box Keywords Only Implementation

**Score: 25/25 | Probability of Success: 95%**

#### Description

Implement only the `<shape-box>` keywords (`margin-box`, `border-box`, `padding-box`, `content-box`) for `shape-outside`, without shape functions. This provides immediate value with minimal implementation effort.

#### Technical Implementation

**Files to Modify:**

**1. `/weasyprint/css/properties.py`** (Add 1 line)
```python
INITIAL_VALUES = {
    ...
    'shape_outside': 'none',
}
```

**2. `/weasyprint/css/validation/properties.py`** (Add ~15 lines)
```python
@property('shape-outside')
@single_keyword
def shape_outside(keyword):
    """Validation for shape-outside property."""
    return keyword in ('none', 'margin-box', 'border-box',
                        'padding-box', 'content-box')
```

**3. `/weasyprint/layout/float.py`** - Modify `avoid_collisions()` (~20 lines changed)
```python
def get_shape_bounds(shape):
    box_type = shape.style.get('shape_outside', 'margin-box')
    if box_type == 'none' or box_type == 'margin-box':
        return (shape.position_x, shape.margin_width())
    elif box_type == 'border-box':
        return (shape.border_box_x(), shape.border_width())
    elif box_type == 'padding-box':
        return (shape.padding_box_x(), shape.padding_width())
    elif box_type == 'content-box':
        return (shape.content_box_x(), shape.width)
```

#### Advantages

- **Extremely low risk**: Uses only existing box model calculations
- **Zero new algorithms**: No geometry code needed
- **Immediate value**: Many designs use shape-outside with just box keywords
- **Foundation for future**: Later solutions can build on this CSS property
- **5-10 lines of core changes**: Minimal code footprint

#### Disadvantages

- **Limited functionality**: No circle, polygon, or image shapes
- **May not satisfy advanced users**: Those wanting complex shapes need more

#### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking existing layouts | None | New property, opt-in only |
| Performance impact | None | Existing calculations |
| Test coverage needed | Minimal | 4 new test cases |

---

### 2. Solution 6: Shape Boundary Function Object

**Score: 22/25 | Probability of Success: 85%**

#### Description

Create a clean object-oriented `ShapeBoundary` abstraction that encapsulates shape evaluation. Each shape type has its own boundary class. The float box stores a boundary object, and `avoid_collisions()` queries it for bounds at any Y coordinate.

#### Technical Implementation

**New File: `/weasyprint/layout/shapes.py`** (~150 lines)

```python
from abc import ABC, abstractmethod
import math

class ShapeBoundary(ABC):
    """Abstract base for shape-outside boundaries."""

    @abstractmethod
    def get_bounds_at_y(self, y: float, box_x: float, box_width: float) -> tuple:
        """Return (left_bound, right_bound) at given y coordinate."""
        pass

    @abstractmethod
    def get_vertical_extent(self) -> tuple:
        """Return (min_y, max_y) of shape."""
        pass


class MarginBoxBoundary(ShapeBoundary):
    """Rectangular boundary using margin box."""

    def __init__(self, box):
        self.box = box

    def get_bounds_at_y(self, y, box_x, box_width):
        return (box_x, box_x + self.box.margin_width())

    def get_vertical_extent(self):
        return (self.box.position_y,
                self.box.position_y + self.box.margin_height())


class CircleBoundary(ShapeBoundary):
    """Circular boundary for circle() function."""

    def __init__(self, cx, cy, radius):
        self.cx, self.cy, self.radius = cx, cy, radius

    def get_bounds_at_y(self, y, box_x, box_width):
        dy = y - self.cy
        if abs(dy) > self.radius:
            return None  # No intersection at this y
        dx = math.sqrt(self.radius**2 - dy**2)
        return (self.cx - dx, self.cx + dx)

    def get_vertical_extent(self):
        return (self.cy - self.radius, self.cy + self.radius)


class EllipseBoundary(ShapeBoundary):
    """Elliptical boundary for ellipse() function."""

    def __init__(self, cx, cy, rx, ry):
        self.cx, self.cy, self.rx, self.ry = cx, cy, rx, ry

    def get_bounds_at_y(self, y, box_x, box_width):
        dy = y - self.cy
        if abs(dy) > self.ry:
            return None
        # Ellipse equation: (x-cx)²/rx² + (y-cy)²/ry² = 1
        ratio = 1 - (dy**2 / self.ry**2)
        if ratio < 0:
            return None
        dx = self.rx * math.sqrt(ratio)
        return (self.cx - dx, self.cx + dx)

    def get_vertical_extent(self):
        return (self.cy - self.ry, self.cy + self.ry)


class PolygonBoundary(ShapeBoundary):
    """Polygon boundary using scanline intersection."""

    def __init__(self, points):
        self.points = points  # [(x1,y1), (x2,y2), ...]
        self._compute_extent()

    def _compute_extent(self):
        ys = [p[1] for p in self.points]
        self.min_y, self.max_y = min(ys), max(ys)

    def get_bounds_at_y(self, y, box_x, box_width):
        if y < self.min_y or y > self.max_y:
            return None

        # Scanline intersection algorithm
        intersections = []
        n = len(self.points)
        for i in range(n):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i + 1) % n]

            if y1 == y2:
                continue  # Horizontal edge
            if not (min(y1, y2) <= y <= max(y1, y2)):
                continue  # Y not in edge range

            # Linear interpolation for x at y
            t = (y - y1) / (y2 - y1)
            x = x1 + t * (x2 - x1)
            intersections.append(x)

        if len(intersections) < 2:
            return None
        intersections.sort()
        return (intersections[0], intersections[-1])

    def get_vertical_extent(self):
        return (self.min_y, self.max_y)
```

**Modify `/weasyprint/layout/float.py`:**

```python
from .shapes import MarginBoxBoundary, CircleBoundary, EllipseBoundary, PolygonBoundary

def float_layout(context, box, ...):
    # After positioning the float, create its shape boundary
    box.shape_boundary = create_shape_boundary(box)
    context.excluded_shapes.append(box)

def create_shape_boundary(box):
    shape_outside = box.style.get('shape_outside', 'none')
    if shape_outside == 'none' or shape_outside == 'margin-box':
        return MarginBoxBoundary(box)
    elif isinstance(shape_outside, tuple) and shape_outside[0] == 'circle':
        _, radius, position = shape_outside
        cx, cy = resolve_position(position, box)
        r = resolve_radius(radius, box)
        return CircleBoundary(cx, cy, r)
    # ... additional shape types
    return MarginBoxBoundary(box)  # Fallback

def avoid_collisions(context, box, ...):
    for shape in excluded_shapes:
        bounds = shape.shape_boundary.get_bounds_at_y(current_y, ...)
        if bounds:
            if shape.style['float'] == 'left':
                left_bounds.append(bounds[1])
            else:
                right_bounds.append(bounds[0])
```

#### Advantages

- **Clean architecture**: Well-separated concerns, easy to understand
- **Extensible**: Adding new shapes is just adding a new class
- **Testable**: Each boundary class can be unit tested in isolation
- **Maintainable**: OOP patterns familiar to Python developers
- **Self-contained**: All geometry logic in one new module

#### Disadvantages

- **More code**: ~150 lines for new module
- **Abstraction overhead**: Extra objects created per float
- **CSS parsing still needed**: Shape function parsing is separate work

#### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking existing layouts | Low | Additive changes only |
| Performance impact | Low | Simple math per line |
| Complexity | Medium | Good documentation needed |

---

### 3. Solution 3: Per-Line Shape Sampling

**Score: 21/25 | Probability of Success: 80%**

#### Description

The most direct approach: for each line's Y position, evaluate the shape function to get the actual exclusion bounds. No precomputation, no complex abstractions—just evaluate the shape where needed.

#### Technical Implementation

**Modify `/weasyprint/layout/float.py`:**

```python
import math

def get_shape_bounds_at_y(shape, y):
    """Evaluate shape-outside at a specific Y coordinate."""
    shape_outside = shape.style.get('shape_outside', 'none')

    # Box keywords
    if shape_outside in ('none', 'margin-box'):
        return (shape.position_x,
                shape.position_x + shape.margin_width(),
                shape.position_y,
                shape.position_y + shape.margin_height())

    if shape_outside == 'content-box':
        return (shape.content_box_x(),
                shape.content_box_x() + shape.width,
                shape.content_box_y(),
                shape.content_box_y() + shape.height)

    if shape_outside == 'padding-box':
        return (shape.padding_box_x(),
                shape.padding_box_x() + shape.padding_width(),
                shape.padding_box_y(),
                shape.padding_box_y() + shape.padding_height())

    if shape_outside == 'border-box':
        return (shape.border_box_x(),
                shape.border_box_x() + shape.border_width(),
                shape.border_box_y(),
                shape.border_box_y() + shape.border_height())

    # Shape functions
    if not isinstance(shape_outside, tuple):
        return None

    shape_type = shape_outside[0]
    box_x = shape.border_box_x()
    box_y = shape.border_box_y()
    box_w = shape.border_width()
    box_h = shape.border_height()

    if shape_type == 'circle':
        _, radius, position = shape_outside
        cx = resolve_position_x(position[0], box_w) + box_x
        cy = resolve_position_y(position[1], box_h) + box_y
        r = resolve_radius(radius, box_w, box_h, cx, cy, box_x, box_y)

        rel_y = y - cy
        if abs(rel_y) > r:
            return None
        dx = math.sqrt(r**2 - rel_y**2)
        return (cx - dx, cx + dx, cy - r, cy + r)

    elif shape_type == 'ellipse':
        _, rx, ry, position = shape_outside
        cx = resolve_position_x(position[0], box_w) + box_x
        cy = resolve_position_y(position[1], box_h) + box_y
        rx_abs = resolve_radius(rx, box_w, box_h, cx, cy, box_x, box_y)
        ry_abs = resolve_radius(ry, box_w, box_h, cx, cy, box_x, box_y)

        rel_y = y - cy
        if abs(rel_y) > ry_abs:
            return None
        ratio = 1 - (rel_y**2 / ry_abs**2)
        dx = rx_abs * math.sqrt(max(0, ratio))
        return (cx - dx, cx + dx, cy - ry_abs, cy + ry_abs)

    elif shape_type == 'polygon':
        _, fill_rule, points = shape_outside
        return polygon_bounds_at_y(points, y, box_x, box_y, box_w, box_h)

    return None


def polygon_bounds_at_y(points, y, box_x, box_y, box_w, box_h):
    """Scanline intersection for polygon."""
    # Resolve percentage points to absolute
    abs_points = []
    for px, py in points:
        ax = resolve_length(px, box_w) + box_x
        ay = resolve_length(py, box_h) + box_y
        abs_points.append((ax, ay))

    # Find Y extent
    ys = [p[1] for p in abs_points]
    min_y, max_y = min(ys), max(ys)

    if y < min_y or y > max_y:
        return None

    # Scanline intersection
    intersections = []
    n = len(abs_points)
    for i in range(n):
        x1, y1 = abs_points[i]
        x2, y2 = abs_points[(i + 1) % n]

        if y1 == y2:
            continue
        if not (min(y1, y2) < y <= max(y1, y2)):
            continue

        t = (y - y1) / (y2 - y1)
        x = x1 + t * (x2 - x1)
        intersections.append(x)

    if len(intersections) < 2:
        return None

    intersections.sort()
    xs = [p[0] for p in abs_points]
    return (intersections[0], intersections[-1], min_y, max_y)
```

#### Advantages

- **Direct mapping to spec**: Algorithm matches CSS Shapes spec closely
- **No precomputation overhead**: Calculate only what's needed
- **Simple mental model**: "Evaluate shape at Y, get bounds"
- **Minimal new code**: ~100 lines of geometry code

#### Disadvantages

- **Repeated evaluation**: Same shape evaluated multiple times per page
- **No caching**: Could be slower for complex polygons
- **Coupled to float code**: Geometry mixed with layout logic

#### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking existing layouts | Low | Additive changes |
| Performance impact | Medium | Cache results if needed |
| Code clarity | Medium | Good comments essential |

---

### 4. Solution 5: Polygon-Only Implementation

**Score: 21/25 | Probability of Success: 80%**

#### Description

Implement only the `polygon()` shape function, as it can represent any shape including approximations of circles and ellipses. Other shape functions gracefully degrade to the margin box.

#### Technical Implementation

**CSS Parsing in `/weasyprint/css/validation/properties.py`:**

```python
@property('shape-outside')
def shape_outside(tokens, base_url=None):
    """Validate shape-outside property."""
    if len(tokens) == 1:
        keyword = get_keyword(tokens[0])
        if keyword in ('none', 'margin-box', 'border-box',
                       'padding-box', 'content-box'):
            return keyword

    # Handle function notation
    if len(tokens) == 1 and tokens[0].type == 'function':
        function = tokens[0]
        if function.lower_name == 'polygon':
            return parse_polygon(function)

    # Unknown shapes degrade to margin-box
    return 'margin-box'


def parse_polygon(function):
    """Parse polygon(fill-rule?, [x y]+) function."""
    arguments = split_on_comma(function.arguments)

    fill_rule = 'nonzero'
    start_idx = 0

    # Check for fill-rule keyword
    if arguments:
        first_arg = remove_whitespace(arguments[0])
        if len(first_arg) == 1:
            keyword = get_keyword(first_arg[0])
            if keyword in ('nonzero', 'evenodd'):
                fill_rule = keyword
                start_idx = 1

    # Parse coordinate pairs
    points = []
    for arg in arguments[start_idx:]:
        tokens = remove_whitespace(arg)
        if len(tokens) != 2:
            return 'margin-box'  # Invalid

        x = get_length(tokens[0], negative=True, percentage=True)
        y = get_length(tokens[1], negative=True, percentage=True)
        if x is None or y is None:
            return 'margin-box'
        points.append((x, y))

    if len(points) < 3:
        return 'margin-box'  # Need at least 3 points

    return ('polygon', fill_rule, tuple(points))
```

**Geometry in `/weasyprint/layout/float.py`:**

```python
def polygon_bounds_at_y(points, y, reference_box):
    """Calculate horizontal bounds of polygon at given Y using scanline."""
    box_x = reference_box.border_box_x()
    box_y = reference_box.border_box_y()
    box_w = reference_box.border_width()
    box_h = reference_box.border_height()

    # Resolve percentage values to absolute coordinates
    abs_points = []
    for px, py in points:
        ax = resolve_length_value(px, box_w) + box_x
        ay = resolve_length_value(py, box_h) + box_y
        abs_points.append((ax, ay))

    # Scanline intersection
    intersections = []
    n = len(abs_points)

    for i in range(n):
        x1, y1 = abs_points[i]
        x2, y2 = abs_points[(i + 1) % n]

        if y1 == y2:
            continue

        if not (min(y1, y2) < y <= max(y1, y2)):
            continue

        t = (y - y1) / (y2 - y1)
        x = x1 + t * (x2 - x1)
        intersections.append(x)

    if not intersections:
        return None

    intersections.sort()
    return (intersections[0], intersections[-1])
```

#### Advantages

- **Maximum flexibility**: Polygons can approximate any shape
- **Simple algorithm**: Scanline intersection is well-understood
- **Single geometry type**: Only one algorithm to implement and test
- **Graceful degradation**: Unknown shapes fall back to margin-box
- **Real-world coverage**: Many shape-outside uses are angular designs

#### Disadvantages

- **No native circle/ellipse**: Users must approximate with polygon points
- **Slightly more verbose CSS**: `polygon(50% 0, 100% 100%, 0 100%)` vs `circle(50%)`
- **Approximation artifacts**: Curved shapes may show polygon edges

#### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking existing layouts | None | New feature only |
| Performance impact | Low | O(n) per line, n = vertices |
| User expectations | Medium | Document limitations |

---

### 5. Solution 8: Circle and Ellipse Basic Shapes

**Score: 21/25 | Probability of Success: 78%**

#### Description

Implement `circle()` and `ellipse()` shape functions only, as they cover the majority of real-world shape-outside use cases and have the simplest geometry.

#### Technical Implementation

**CSS Parsing:**

```python
@property('shape-outside')
def shape_outside(tokens, base_url=None):
    """Validate shape-outside property."""
    if len(tokens) == 1:
        keyword = get_keyword(tokens[0])
        if keyword in ('none', 'margin-box', 'border-box',
                       'padding-box', 'content-box'):
            return keyword

    if len(tokens) == 1 and tokens[0].type == 'function':
        function = tokens[0]
        if function.lower_name == 'circle':
            return parse_circle(function)
        elif function.lower_name == 'ellipse':
            return parse_ellipse(function)

    return 'margin-box'  # Fallback


def parse_circle(function):
    """Parse circle(radius? at position?) function."""
    args = list(remove_whitespace(function.arguments))

    radius = ('closest-side',)
    position = (('percentage', 50), ('percentage', 50))

    # Find 'at' keyword
    at_index = None
    for i, token in enumerate(args):
        if get_keyword(token) == 'at':
            at_index = i
            break

    if at_index is not None:
        radius_tokens = args[:at_index]
        position_tokens = args[at_index + 1:]
    else:
        radius_tokens = args
        position_tokens = []

    # Parse radius
    if radius_tokens:
        keyword = get_keyword(radius_tokens[0])
        if keyword in ('closest-side', 'farthest-side'):
            radius = (keyword,)
        else:
            length = get_length(radius_tokens[0], percentage=True)
            if length:
                radius = length

    # Parse position
    if position_tokens:
        pos = parse_2d_position(position_tokens)
        if pos:
            position = pos

    return ('circle', radius, position)


def parse_ellipse(function):
    """Parse ellipse(rx ry? at position?) function."""
    args = list(remove_whitespace(function.arguments))

    rx = ('closest-side',)
    ry = ('closest-side',)
    position = (('percentage', 50), ('percentage', 50))

    at_index = None
    for i, token in enumerate(args):
        if get_keyword(token) == 'at':
            at_index = i
            break

    if at_index is not None:
        radii_tokens = args[:at_index]
        position_tokens = args[at_index + 1:]
    else:
        radii_tokens = args
        position_tokens = []

    # Parse radii
    if len(radii_tokens) >= 1:
        rx = parse_ellipse_radius(radii_tokens[0])
    if len(radii_tokens) >= 2:
        ry = parse_ellipse_radius(radii_tokens[1])

    if position_tokens:
        pos = parse_2d_position(position_tokens)
        if pos:
            position = pos

    return ('ellipse', rx, ry, position)
```

**Geometry Functions:**

```python
import math

def circle_bounds_at_y(radius, center, y, reference_box):
    """Calculate circle bounds at Y coordinate."""
    box_x = reference_box.border_box_x()
    box_y = reference_box.border_box_y()
    box_w = reference_box.border_width()
    box_h = reference_box.border_height()

    # Resolve center
    cx = resolve_position_value(center[0], box_w) + box_x
    cy = resolve_position_value(center[1], box_h) + box_y

    # Resolve radius
    if isinstance(radius, tuple):
        if radius[0] == 'closest-side':
            r = min(cx - box_x, box_x + box_w - cx,
                    cy - box_y, box_y + box_h - cy)
        elif radius[0] == 'farthest-side':
            r = max(cx - box_x, box_x + box_w - cx,
                    cy - box_y, box_y + box_h - cy)
    else:
        # Percentage resolves against sqrt(width² + height²) / sqrt(2)
        ref = math.sqrt(box_w**2 + box_h**2) / math.sqrt(2)
        r = resolve_length_value(radius, ref)

    # Calculate intersection
    dy = y - cy
    if abs(dy) > r:
        return None

    dx = math.sqrt(r * r - dy * dy)
    return (cx - dx, cx + dx)


def ellipse_bounds_at_y(rx, ry, center, y, reference_box):
    """Calculate ellipse bounds at Y coordinate."""
    box_x = reference_box.border_box_x()
    box_y = reference_box.border_box_y()
    box_w = reference_box.border_width()
    box_h = reference_box.border_height()

    cx = resolve_position_value(center[0], box_w) + box_x
    cy = resolve_position_value(center[1], box_h) + box_y

    rx_abs = resolve_ellipse_radius(rx, box_w, cx - box_x)
    ry_abs = resolve_ellipse_radius(ry, box_h, cy - box_y)

    dy = y - cy
    if abs(dy) > ry_abs:
        return None

    ratio = 1 - (dy * dy) / (ry_abs * ry_abs)
    dx = rx_abs * math.sqrt(max(0, ratio))

    return (cx - dx, cx + dx)
```

#### Advantages

- **Covers common use cases**: Circles and ovals are very common in designs
- **Simple math**: Circle/ellipse geometry is straightforward
- **Good CSS alignment**: These are the most readable shape functions
- **Natural positioning**: `at center`, `at top left` syntax is intuitive
- **Keyword radii**: `closest-side`, `farthest-side` are useful defaults

#### Disadvantages

- **No polygon support**: Can't do angular or complex shapes
- **No path support**: Advanced SVG-style paths not available
- **Incomplete spec**: Users familiar with full spec may be confused

#### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Breaking existing layouts | None | New feature only |
| Performance impact | Very Low | Simple math operations |
| Feature completeness | Medium | Covers ~60% of use cases |

---

## Implementation Recommendation

### Phased Approach

We recommend a phased implementation that delivers value incrementally while minimizing risk:

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4
(Box KW)    (OOP Base)  (Shapes)    (Advanced)
```

#### Phase 1: Box Keywords (Solution 1)
**Timeline: Immediate**

- Implement `margin-box`, `border-box`, `padding-box`, `content-box`
- ~25 lines of code changes
- Nearly zero risk
- Provides immediate value

#### Phase 2: Architecture Foundation (Solution 6 base)
**Timeline: Short-term**

- Create `ShapeBoundary` abstraction with `MarginBoxBoundary`
- ~80 lines of new code
- Sets up extensible architecture
- No functional change yet

#### Phase 3: Basic Shapes (Solutions 8 + 5)
**Timeline: Medium-term**

- Add `CircleBoundary` and `EllipseBoundary` (most common)
- Add `PolygonBoundary` for advanced users
- ~150 lines of geometry code
- Covers 90%+ of use cases

#### Phase 4: Advanced Features
**Timeline: Long-term (as needed)**

- `InsetBoundary` for `inset()` function
- `PathBoundary` for `path()` function
- Image-based shapes via alpha channel
- `shape-margin` property

### Files Changed Summary

| Phase | Files Modified | Lines Added | Risk Level |
|-------|---------------|-------------|------------|
| 1 | 3 files | ~25 lines | Very Low |
| 2 | 2 files | ~80 lines | Low |
| 3 | 2 files | ~150 lines | Low-Medium |
| 4 | 3+ files | ~200+ lines | Medium |

### Key Integration Points

1. **CSS Property**: `/weasyprint/css/properties.py` - Add `shape_outside` to `INITIAL_VALUES`

2. **CSS Validation**: `/weasyprint/css/validation/properties.py` - Add `@property('shape-outside')` validator

3. **Float Layout**: `/weasyprint/layout/float.py` - Modify `avoid_collisions()` to query shape bounds

4. **New Module**: `/weasyprint/layout/shapes.py` - Shape boundary classes (Phase 2+)

### Testing Strategy

Each phase should include:

1. **Unit tests** for geometry calculations (circle intersection, polygon scanline)
2. **Integration tests** for CSS parsing
3. **Visual regression tests** comparing output to browser rendering
4. **Performance benchmarks** for pages with many floats

---

## Conclusion

The CSS `shape-outside` property can be added to WeasyPrint through a carefully phased approach that:

- **Delivers immediate value** with box keywords (Solution 1)
- **Establishes clean architecture** with shape boundary objects (Solution 6)
- **Covers common use cases** with circle/ellipse support (Solution 8)
- **Enables advanced layouts** with polygon support (Solution 5)

This approach ensures:

- ✅ No new dependencies (uses only stdlib `math` module)
- ✅ Minimal risk at each phase
- ✅ Clean, maintainable code architecture
- ✅ Incremental feature delivery
- ✅ Full CSS Shapes Level 1 support over time

The recommended starting point is **Solution 1 (Box Keywords Only)**, which provides immediate value with approximately 25 lines of code changes and near-zero risk of breaking existing functionality.
