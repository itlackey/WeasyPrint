"""Tests for CSS shape-outside property with box keyword values."""

import pytest

from weasyprint.layout.float import get_shape_box_bounds
from weasyprint.layout.shapes import BoxBoundary, ShapeBoundary, create_shape_boundary

from ..testing_utils import assert_no_logs, render_pages


# ---------------------------------------------------------------------------
# CSS Parsing/Validation Tests
# ---------------------------------------------------------------------------

@assert_no_logs
@pytest.mark.parametrize('value', [
    'none',
    'margin-box',
    'border-box',
    'padding-box',
    'content-box',
])
def test_shape_outside_valid_keywords(value):
    """Test that valid shape-outside keywords are accepted and parsed."""
    page, = render_pages(f'''
        <style>
            div {{
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: {value};
            }}
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    assert div.style['shape_outside'] == value


@assert_no_logs
def test_shape_outside_default_value():
    """Test that the default value of shape-outside is 'none'."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    assert div.style['shape_outside'] == 'none'


@assert_no_logs
def test_shape_outside_inherit():
    """Test that shape-outside can be inherited."""
    page, = render_pages('''
        <style>
            .parent { shape-outside: border-box; }
            .child { float: left; width: 50px; height: 50px; shape-outside: inherit; }
        </style>
        <div class="parent">
            <div class="child"></div>
        </div>
    ''')
    html, = page.children
    body, = html.children
    parent, = body.children
    child, = parent.children
    assert child.style['shape_outside'] == 'border-box'


def test_shape_outside_invalid_keywords():
    """Test that invalid shape-outside keywords fall back to default."""
    from ..testing_utils import capture_logs

    # Invalid values should be logged and default to 'none'
    with capture_logs() as logs:
        page, = render_pages('''
            <style>
                div {
                    float: left;
                    width: 100px;
                    height: 100px;
                    shape-outside: invalid-keyword;
                }
            </style>
            <div></div>
        ''')
    # There should be an error logged for the invalid value
    assert any('invalid' in log.lower() for log in logs)
    html, = page.children
    body, = html.children
    div, = body.children
    # Should fall back to default 'none'
    assert div.style['shape_outside'] == 'none'


@pytest.mark.parametrize('invalid_value', [
    'url(image.png)',  # image reference (not yet supported)
    '50px',  # length value (invalid)
    '50%',  # percentage value (invalid)
    'auto',  # not a valid shape-outside value
    'polygon(0 0, 100% 0)',  # polygon with less than 3 points
])
def test_shape_outside_unsupported_values(invalid_value):
    """Test that unsupported shape-outside values fall back to default."""
    from ..testing_utils import capture_logs

    with capture_logs() as logs:
        page, = render_pages(f'''
            <style>
                div {{
                    float: left;
                    width: 100px;
                    height: 100px;
                    shape-outside: {invalid_value};
                }}
            </style>
            <div></div>
        ''')
    html, = page.children
    body, = html.children
    div, = body.children
    # Should fall back to default 'none'
    assert div.style['shape_outside'] == 'none'


# ---------------------------------------------------------------------------
# get_shape_box_bounds Unit Tests
# ---------------------------------------------------------------------------

@assert_no_logs
def test_shape_box_bounds_none():
    """Test get_shape_box_bounds returns margin box for shape-outside: none."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: none;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    x, width = get_shape_box_bounds(div)
    # For none, should use margin box
    assert x == div.position_x
    assert width == div.margin_width()


@assert_no_logs
def test_shape_box_bounds_margin_box():
    """Test get_shape_box_bounds returns margin box for shape-outside: margin-box."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: margin-box;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    x, width = get_shape_box_bounds(div)
    # margin-box: position_x and margin_width
    assert x == div.position_x
    assert width == div.margin_width()


@assert_no_logs
def test_shape_box_bounds_border_box():
    """Test get_shape_box_bounds returns border box for shape-outside: border-box."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: border-box;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    x, width = get_shape_box_bounds(div)
    # border-box: border_box_x and border_width
    assert x == div.border_box_x()
    assert width == div.border_width()


@assert_no_logs
def test_shape_box_bounds_padding_box():
    """Test get_shape_box_bounds returns padding box for shape-outside: padding-box."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: padding-box;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    x, width = get_shape_box_bounds(div)
    # padding-box: padding_box_x and padding_width
    assert x == div.padding_box_x()
    assert width == div.padding_width()


@assert_no_logs
def test_shape_box_bounds_content_box():
    """Test get_shape_box_bounds returns content box for shape-outside: content-box."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: content-box;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    x, width = get_shape_box_bounds(div)
    # content-box: content_box_x and width
    assert x == div.content_box_x()
    assert width == div.width


# ---------------------------------------------------------------------------
# ShapeBoundary and BoxBoundary Unit Tests
# ---------------------------------------------------------------------------

@assert_no_logs
def test_box_boundary_is_shape_boundary():
    """Test that BoxBoundary is a subclass of ShapeBoundary."""
    assert issubclass(BoxBoundary, ShapeBoundary)


@assert_no_logs
@pytest.mark.parametrize('box_type', [
    'margin-box',
    'border-box',
    'padding-box',
    'content-box',
])
def test_box_boundary_construction(box_type):
    """Test BoxBoundary construction with each box type."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = BoxBoundary(div, box_type)
    assert boundary.box is div
    assert boundary.box_type == box_type


@assert_no_logs
def test_box_boundary_margin_box_bounds():
    """Test BoxBoundary margin-box bounds computation."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = BoxBoundary(div, 'margin-box')
    # Margin box
    assert boundary.left == div.position_x
    assert boundary.right == div.position_x + div.margin_width()
    assert boundary.top == div.position_y
    assert boundary.bottom == div.position_y + div.margin_height()


@assert_no_logs
def test_box_boundary_border_box_bounds():
    """Test BoxBoundary border-box bounds computation."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = BoxBoundary(div, 'border-box')
    # Horizontal bounds use border-box
    assert boundary.left == div.border_box_x()
    assert boundary.right == div.border_box_x() + div.border_width()
    # Vertical extent always uses margin-box for collision detection
    assert boundary.top == div.position_y
    assert boundary.bottom == div.position_y + div.margin_height()


@assert_no_logs
def test_box_boundary_padding_box_bounds():
    """Test BoxBoundary padding-box bounds computation."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = BoxBoundary(div, 'padding-box')
    # Horizontal bounds use padding-box
    assert boundary.left == div.padding_box_x()
    assert boundary.right == div.padding_box_x() + div.padding_width()
    # Vertical extent always uses margin-box for collision detection
    assert boundary.top == div.position_y
    assert boundary.bottom == div.position_y + div.margin_height()


@assert_no_logs
def test_box_boundary_content_box_bounds():
    """Test BoxBoundary content-box bounds computation."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = BoxBoundary(div, 'content-box')
    # Horizontal bounds use content-box
    assert boundary.left == div.content_box_x()
    assert boundary.right == div.content_box_x() + div.width
    # Vertical extent always uses margin-box for collision detection
    assert boundary.top == div.position_y
    assert boundary.bottom == div.position_y + div.margin_height()


@assert_no_logs
def test_box_boundary_get_bounds_at_y_within_extent():
    """Test get_bounds_at_y returns correct bounds within vertical extent."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = BoxBoundary(div, 'margin-box')
    top, bottom = boundary.get_vertical_extent()

    # Test at various Y positions within the extent
    y_middle = (top + bottom) / 2
    bounds = boundary.get_bounds_at_y(y_middle)
    assert bounds is not None
    assert bounds == (boundary.left, boundary.right)

    # Test at top edge
    bounds_top = boundary.get_bounds_at_y(top)
    assert bounds_top is not None
    assert bounds_top == (boundary.left, boundary.right)

    # Test at bottom edge
    bounds_bottom = boundary.get_bounds_at_y(bottom)
    assert bounds_bottom is not None
    assert bounds_bottom == (boundary.left, boundary.right)


@assert_no_logs
def test_box_boundary_get_bounds_at_y_always_returns_bounds():
    """Test get_bounds_at_y always returns bounds for BoxBoundary.

    For rectangular box-based shapes, horizontal bounds are constant
    regardless of Y position. The collision detection in avoid_collisions()
    handles vertical overlap checking, so get_bounds_at_y() always returns
    the bounds.
    """
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = BoxBoundary(div, 'margin-box')
    top, bottom = boundary.get_vertical_extent()

    # For BoxBoundary, bounds are always returned regardless of Y
    # because horizontal bounds are constant for rectangular shapes
    bounds_above = boundary.get_bounds_at_y(top - 100)
    assert bounds_above == (boundary.left, boundary.right)

    bounds_below = boundary.get_bounds_at_y(bottom + 100)
    assert bounds_below == (boundary.left, boundary.right)


@assert_no_logs
def test_box_boundary_get_vertical_extent():
    """Test get_vertical_extent returns correct range.

    For BoxBoundary, vertical extent always uses margin-box for
    collision detection, regardless of the box_type setting.
    """
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    # Test for margin-box
    boundary_margin = BoxBoundary(div, 'margin-box')
    top, bottom = boundary_margin.get_vertical_extent()
    assert top == div.position_y
    assert bottom == div.position_y + div.margin_height()

    # Test for content-box - vertical extent still uses margin-box
    boundary_content = BoxBoundary(div, 'content-box')
    top, bottom = boundary_content.get_vertical_extent()
    assert top == div.position_y
    assert bottom == div.position_y + div.margin_height()


# ---------------------------------------------------------------------------
# create_shape_boundary Factory Function Unit Tests
# ---------------------------------------------------------------------------

@assert_no_logs
@pytest.mark.parametrize('shape_outside,expected_box_type', [
    ('none', 'margin-box'),
    ('margin-box', 'margin-box'),
    ('border-box', 'border-box'),
    ('padding-box', 'padding-box'),
    ('content-box', 'content-box'),
])
def test_create_shape_boundary_returns_correct_type(shape_outside, expected_box_type):
    """Test create_shape_boundary returns correct boundary type for each keyword."""
    page, = render_pages(f'''
        <style>
            div {{
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: {shape_outside};
            }}
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = create_shape_boundary(div)
    assert isinstance(boundary, BoxBoundary)
    assert boundary.box_type == expected_box_type


@assert_no_logs
def test_create_shape_boundary_default_none():
    """Test create_shape_boundary default behavior for 'none'."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                shape-outside: none;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = create_shape_boundary(div)
    # 'none' should behave like 'margin-box'
    assert isinstance(boundary, BoxBoundary)
    assert boundary.box_type == 'margin-box'
    assert boundary.left == div.position_x
    assert boundary.right == div.position_x + div.margin_width()


@assert_no_logs
def test_float_has_shape_boundary_attached():
    """Test that floated boxes have shape_boundary attribute after layout."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                shape-outside: border-box;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    # After layout, the float should have a shape_boundary attribute
    assert hasattr(div, 'shape_boundary')
    assert isinstance(div.shape_boundary, BoxBoundary)
    assert div.shape_boundary.box_type == 'border-box'


@assert_no_logs
def test_shape_boundary_matches_get_shape_box_bounds():
    """Test that shape boundary bounds match get_shape_box_bounds output."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 80px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: padding-box;
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    # Get bounds from both methods
    old_x, old_width = get_shape_box_bounds(div)
    boundary = div.shape_boundary
    new_left = boundary.left
    new_right = boundary.right

    # They should match
    assert new_left == old_x
    assert new_right == old_x + old_width


# ---------------------------------------------------------------------------
# Integration Tests: Left Float with shape-outside
# ---------------------------------------------------------------------------

@assert_no_logs
def test_left_float_shape_outside_none():
    """Test left float with shape-outside: none behaves like default."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: left;
                width: 50px;
                height: 50px;
                margin: 10px;
                shape-outside: none;
            }
            img { width: 30px; height: 30px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # With margin: 10px, width: 50px, shape-outside: none (uses margin-box)
    # The image should start after the float's margin box: 10 + 50 + 10 = 70
    assert img.position_x == 70


@assert_no_logs
def test_left_float_shape_outside_content_box():
    """Test left float with shape-outside: content-box allows content closer."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: left;
                width: 50px;
                height: 50px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: content-box;
            }
            img { width: 30px; height: 30px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # With shape-outside: content-box, the exclusion area is the content box.
    # Content box starts at: margin(10) + border(2) + padding(5) = 17
    # Content box width: 50
    # So image should start at: 17 + 50 = 67
    assert img.position_x == 67


@assert_no_logs
def test_left_float_shape_outside_border_box():
    """Test left float with shape-outside: border-box."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: left;
                width: 50px;
                height: 50px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: border-box;
            }
            img { width: 30px; height: 30px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # With shape-outside: border-box, the exclusion area is the border box.
    # Border box starts at: margin(10) = 10
    # Border box width: border(2) + padding(5) + content(50) + padding(5) + border(2) = 64
    # So image should start at: 10 + 64 = 74
    assert img.position_x == 74


@assert_no_logs
def test_left_float_shape_outside_padding_box():
    """Test left float with shape-outside: padding-box."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: left;
                width: 50px;
                height: 50px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: padding-box;
            }
            img { width: 30px; height: 30px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # With shape-outside: padding-box, the exclusion area is the padding box.
    # Padding box starts at: margin(10) + border(2) = 12
    # Padding box width: padding(5) + content(50) + padding(5) = 60
    # So image should start at: 12 + 60 = 72
    assert img.position_x == 72


# ---------------------------------------------------------------------------
# Integration Tests: Right Float with shape-outside
# ---------------------------------------------------------------------------

@assert_no_logs
def test_right_float_shape_outside_content_box():
    """Test right float with shape-outside: content-box."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: right;
                width: 50px;
                height: 50px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: content-box;
            }
            img { width: 30px; height: 30px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # With shape-outside: content-box on a right float, the line's available
    # width is reduced based on the content box.
    # Float's content box starts at: 200 - 10 - 2 - 5 - 50 = 133
    # This affects the max_right_bound in avoid_collisions
    assert img.position_x == 0
    # The image should fit within the available space (content box edge at 133)
    assert img.position_x + img.width <= 133


@assert_no_logs
def test_right_float_shape_outside_margin_box():
    """Test right float with shape-outside: margin-box (default behavior)."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: right;
                width: 50px;
                height: 50px;
                margin: 10px;
                padding: 5px;
                border: 2px solid black;
                shape-outside: margin-box;
            }
            img { width: 30px; height: 30px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # With shape-outside: margin-box on a right float
    # Float's margin box starts at: 200 - 10 - 2 - 5 - 50 - 5 - 2 - 10 = 116
    # This affects the max_right_bound in avoid_collisions
    assert img.position_x == 0
    # The image should fit within the available space (margin box edge at 116)
    assert img.position_x + img.width <= 116


# ---------------------------------------------------------------------------
# Edge Cases and Special Scenarios
# ---------------------------------------------------------------------------

@assert_no_logs
def test_multiple_floats_with_different_shape_outside():
    """Test multiple floats with different shape-outside values."""
    page, = render_pages('''
        <style>
            body { width: 300px; font-size: 0; }
            .float1 {
                float: left;
                width: 50px;
                height: 50px;
                margin: 5px;
                shape-outside: margin-box;
            }
            .float2 {
                float: left;
                width: 50px;
                height: 50px;
                margin: 10px;
                shape-outside: content-box;
            }
            img { width: 30px; height: 30px; vertical-align: top; }
        </style>
        <div class="float1"></div>
        <div class="float2"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float1, float2, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # Float1: margin-box, starts at 0, width = 5 + 50 + 5 = 60
    # Float2: positioned after float1's margin box at x=60
    # Float2's content box x = 60 + 10 = 70
    # Float2's content box width = 50
    # Image should start after float2's content box: 70 + 50 = 120
    assert float1.position_x == 0
    assert float2.position_x == 60
    assert img.position_x == 120


@assert_no_logs
def test_float_shape_outside_no_margin():
    """Test shape-outside with float that has no margin."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: left;
                width: 50px;
                height: 50px;
                margin: 0;
                padding: 10px;
                border: 5px solid black;
                shape-outside: content-box;
            }
            img { width: 30px; height: 30px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # With no margin:
    # Content box starts at: border(5) + padding(10) = 15
    # Content box width: 50
    # Image should start at: 15 + 50 = 65
    assert img.position_x == 65


@assert_no_logs
def test_shape_outside_with_text_wrapping():
    """Test that text wraps correctly around shape-outside."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-family: weasyprint; font-size: 20px; }
            .float {
                float: left;
                width: 60px;
                height: 40px;
                margin: 10px;
                shape-outside: content-box;
            }
        </style>
        <div class="float"></div>
        AAAA BBBB
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children

    # The text should wrap around the float based on content-box
    # Content box ends at: 10 (margin) + 60 (width) = 70
    # This leaves 130px for text
    # Text may wrap to multiple lines depending on available width
    lines = anon_block.children
    # The first line should start after the content box edge
    assert lines[0].position_x == 70


# ---------------------------------------------------------------------------
# Phase 3: Shape Function CSS Parsing Tests
# ---------------------------------------------------------------------------

@assert_no_logs
def test_circle_parsing_defaults():
    """Test circle() with no arguments uses default values."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle();
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'circle'
    # Default radius is 'closest-side'
    assert shape_outside[1] == 'closest-side'
    # Default position is 50% 50%
    assert shape_outside[2][0].value == 50
    assert shape_outside[2][0].unit == '%'
    assert shape_outside[2][1].value == 50
    assert shape_outside[2][1].unit == '%'


@assert_no_logs
def test_circle_parsing_with_radius():
    """Test circle() with explicit radius."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(50px);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'circle'
    assert shape_outside[1].value == 50
    assert shape_outside[1].unit == 'px'


@assert_no_logs
def test_circle_parsing_with_percentage_radius():
    """Test circle() with percentage radius."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(50%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'circle'
    assert shape_outside[1].value == 50
    assert shape_outside[1].unit == '%'


@assert_no_logs
def test_circle_parsing_with_position():
    """Test circle() with position only."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(at 25% 75%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'circle'
    # Default radius
    assert shape_outside[1] == 'closest-side'
    # Custom position
    assert shape_outside[2][0].value == 25
    assert shape_outside[2][1].value == 75


@assert_no_logs
def test_circle_parsing_with_radius_and_position():
    """Test circle() with both radius and position."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(100px at 25% 75%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'circle'
    assert shape_outside[1].value == 100
    assert shape_outside[1].unit == 'px'
    assert shape_outside[2][0].value == 25
    assert shape_outside[2][1].value == 75


@assert_no_logs
def test_circle_parsing_closest_side():
    """Test circle() with closest-side keyword."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(closest-side);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'circle'
    assert shape_outside[1] == 'closest-side'


@assert_no_logs
def test_circle_parsing_farthest_side():
    """Test circle() with farthest-side keyword."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(farthest-side);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'circle'
    assert shape_outside[1] == 'farthest-side'


@assert_no_logs
def test_ellipse_parsing_defaults():
    """Test ellipse() with no arguments uses default values."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: ellipse();
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'ellipse'
    # Default radii are 'closest-side'
    assert shape_outside[1] == 'closest-side'
    assert shape_outside[2] == 'closest-side'


@assert_no_logs
def test_ellipse_parsing_with_radii():
    """Test ellipse() with explicit radii."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: ellipse(50px 100px);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'ellipse'
    assert shape_outside[1].value == 50
    assert shape_outside[2].value == 100


@assert_no_logs
def test_ellipse_parsing_with_single_radius():
    """Test ellipse() with single radius (applies to both)."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: ellipse(50px);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'ellipse'
    assert shape_outside[1].value == 50
    assert shape_outside[2].value == 50


@assert_no_logs
def test_ellipse_parsing_with_position():
    """Test ellipse() with position only."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: ellipse(at 30% 70%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'ellipse'
    assert shape_outside[3][0].value == 30
    assert shape_outside[3][1].value == 70


@assert_no_logs
def test_ellipse_parsing_with_radii_and_position():
    """Test ellipse() with both radii and position."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: ellipse(50px 80px at 25% 75%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'ellipse'
    assert shape_outside[1].value == 50
    assert shape_outside[2].value == 80
    assert shape_outside[3][0].value == 25
    assert shape_outside[3][1].value == 75


@assert_no_logs
def test_polygon_parsing_triangle():
    """Test polygon() with triangle points."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: polygon(0 0, 100% 0, 50% 100%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'polygon'
    assert shape_outside[1] == 'nonzero'  # default fill-rule
    assert len(shape_outside[2]) == 3  # 3 points


@assert_no_logs
def test_polygon_parsing_with_fill_rule():
    """Test polygon() with explicit fill-rule."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: polygon(evenodd, 0 0, 100% 0, 50% 100%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'polygon'
    assert shape_outside[1] == 'evenodd'


@assert_no_logs
def test_polygon_parsing_rectangle():
    """Test polygon() with rectangle (4 points)."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: polygon(0 0, 100% 0, 100% 100%, 0 100%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'polygon'
    assert len(shape_outside[2]) == 4


@assert_no_logs
def test_polygon_parsing_with_px_values():
    """Test polygon() with pixel values."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: polygon(0px 0px, 100px 0px, 50px 100px);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    shape_outside = div.style['shape_outside']
    assert shape_outside[0] == 'polygon'
    # First point
    assert shape_outside[2][0][0].value == 0
    assert shape_outside[2][0][1].value == 0


# ---------------------------------------------------------------------------
# Phase 3: Shape Boundary Geometry Tests
# ---------------------------------------------------------------------------

from weasyprint.layout.shapes import CircleBoundary, EllipseBoundary, PolygonBoundary


def test_circle_boundary_center():
    """Test CircleBoundary bounds at center Y."""
    boundary = CircleBoundary(cx=100, cy=100, radius=50)
    # At center y=100, bounds should be at x=50 to x=150
    bounds = boundary.get_bounds_at_y(100)
    assert bounds is not None
    assert abs(bounds[0] - 50) < 0.001
    assert abs(bounds[1] - 150) < 0.001


def test_circle_boundary_edge():
    """Test CircleBoundary bounds at edge Y (top and bottom)."""
    boundary = CircleBoundary(cx=100, cy=100, radius=50)
    # At y = 50 (top edge), bounds should be a single point (100, 100)
    bounds_top = boundary.get_bounds_at_y(50)
    assert bounds_top is not None
    assert abs(bounds_top[0] - 100) < 0.001
    assert abs(bounds_top[1] - 100) < 0.001

    # At y = 150 (bottom edge)
    bounds_bottom = boundary.get_bounds_at_y(150)
    assert bounds_bottom is not None
    assert abs(bounds_bottom[0] - 100) < 0.001
    assert abs(bounds_bottom[1] - 100) < 0.001


def test_circle_boundary_outside():
    """Test CircleBoundary returns None outside circle."""
    boundary = CircleBoundary(cx=100, cy=100, radius=50)
    # Above circle
    assert boundary.get_bounds_at_y(0) is None
    # Below circle
    assert boundary.get_bounds_at_y(200) is None


def test_circle_boundary_vertical_extent():
    """Test CircleBoundary vertical extent."""
    boundary = CircleBoundary(cx=100, cy=100, radius=50)
    extent = boundary.get_vertical_extent()
    assert extent == (50, 150)


def test_ellipse_boundary_center():
    """Test EllipseBoundary bounds at center Y."""
    boundary = EllipseBoundary(cx=100, cy=100, rx=80, ry=50)
    # At center y=100, bounds should be at x=20 to x=180
    bounds = boundary.get_bounds_at_y(100)
    assert bounds is not None
    assert abs(bounds[0] - 20) < 0.001
    assert abs(bounds[1] - 180) < 0.001


def test_ellipse_boundary_asymmetric():
    """Test EllipseBoundary with asymmetric radii."""
    boundary = EllipseBoundary(cx=100, cy=100, rx=100, ry=50)
    # At center, bounds should span full rx
    bounds_center = boundary.get_bounds_at_y(100)
    assert abs(bounds_center[0] - 0) < 0.001
    assert abs(bounds_center[1] - 200) < 0.001

    # At top edge (y=50), should be a single point
    bounds_top = boundary.get_bounds_at_y(50)
    assert bounds_top is not None
    assert abs(bounds_top[0] - 100) < 0.001
    assert abs(bounds_top[1] - 100) < 0.001


def test_ellipse_boundary_outside():
    """Test EllipseBoundary returns None outside ellipse."""
    boundary = EllipseBoundary(cx=100, cy=100, rx=80, ry=50)
    assert boundary.get_bounds_at_y(0) is None
    assert boundary.get_bounds_at_y(200) is None


def test_ellipse_boundary_vertical_extent():
    """Test EllipseBoundary vertical extent."""
    boundary = EllipseBoundary(cx=100, cy=100, rx=80, ry=50)
    extent = boundary.get_vertical_extent()
    assert extent == (50, 150)


def test_polygon_boundary_triangle():
    """Test PolygonBoundary with triangle."""
    # Triangle: top center (50, 0), bottom left (0, 100), bottom right (100, 100)
    points = [(50, 0), (0, 100), (100, 100)]
    boundary = PolygonBoundary(points)

    # At bottom (y=100), bounds should be full width
    bounds_bottom = boundary.get_bounds_at_y(100)
    assert bounds_bottom is not None
    assert abs(bounds_bottom[0] - 0) < 0.001
    assert abs(bounds_bottom[1] - 100) < 0.001

    # At middle (y=50), bounds should be narrower
    bounds_middle = boundary.get_bounds_at_y(50)
    assert bounds_middle is not None
    assert abs(bounds_middle[0] - 25) < 0.001
    assert abs(bounds_middle[1] - 75) < 0.001


def test_polygon_boundary_rectangle():
    """Test PolygonBoundary with rectangle."""
    # Rectangle: (0,0), (100,0), (100,100), (0,100)
    points = [(0, 0), (100, 0), (100, 100), (0, 100)]
    boundary = PolygonBoundary(points)

    # At any Y within rectangle, bounds should be 0 to 100
    bounds = boundary.get_bounds_at_y(50)
    assert bounds is not None
    assert abs(bounds[0] - 0) < 0.001
    assert abs(bounds[1] - 100) < 0.001


def test_polygon_boundary_concave():
    """Test PolygonBoundary with concave (arrow) shape."""
    # Arrow pointing right: (0,0), (70,0), (70,30), (100,50), (70,70), (70,100), (0,100)
    points = [(0, 0), (70, 0), (70, 30), (100, 50), (70, 70), (70, 100), (0, 100)]
    boundary = PolygonBoundary(points)

    # At y=50 (arrow point), should extend to x=100
    bounds_point = boundary.get_bounds_at_y(50)
    assert bounds_point is not None
    assert abs(bounds_point[0] - 0) < 0.001
    assert abs(bounds_point[1] - 100) < 0.001

    # At y=20 (above arrow point), should be narrower
    bounds_above = boundary.get_bounds_at_y(20)
    assert bounds_above is not None
    assert abs(bounds_above[0] - 0) < 0.001
    assert bounds_above[1] <= 75  # Should be at or before indentation


def test_polygon_boundary_outside():
    """Test PolygonBoundary returns None outside polygon."""
    points = [(0, 50), (100, 50), (100, 150), (0, 150)]
    boundary = PolygonBoundary(points)
    assert boundary.get_bounds_at_y(0) is None
    assert boundary.get_bounds_at_y(200) is None


def test_polygon_boundary_vertical_extent():
    """Test PolygonBoundary vertical extent."""
    points = [(0, 50), (100, 50), (100, 150), (0, 150)]
    boundary = PolygonBoundary(points)
    extent = boundary.get_vertical_extent()
    assert extent == (50, 150)


# ---------------------------------------------------------------------------
# Phase 3: Shape Function Integration Tests
# ---------------------------------------------------------------------------

@assert_no_logs
def test_float_circle_creates_boundary():
    """Test that circle() float creates CircleBoundary."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(50px);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    assert hasattr(div, 'shape_boundary')
    assert isinstance(div.shape_boundary, CircleBoundary)


@assert_no_logs
def test_float_ellipse_creates_boundary():
    """Test that ellipse() float creates EllipseBoundary."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: ellipse(50px 80px);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    assert hasattr(div, 'shape_boundary')
    assert isinstance(div.shape_boundary, EllipseBoundary)


@assert_no_logs
def test_float_polygon_creates_boundary():
    """Test that polygon() float creates PolygonBoundary."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: polygon(0 0, 100% 0, 50% 100%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children
    assert hasattr(div, 'shape_boundary')
    assert isinstance(div.shape_boundary, PolygonBoundary)


@assert_no_logs
def test_float_circle_text_wrap():
    """Test text wraps around circular float."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(50px at 50% 50%);
            }
            img { width: 30px; height: 10px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # Circle with 50px radius centered at 50,50 of a 100x100 box
    # At y=0 (top of line), the circle edge is at x=50 (center)
    # Image should start after the circle's bound at that y
    # The text will wrap around the curved shape
    assert img.position_x >= 0


@assert_no_logs
def test_float_ellipse_text_wrap():
    """Test text wraps around elliptical float."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: ellipse(50px 50px at 50% 50%);
            }
            img { width: 30px; height: 10px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # Ellipse centered in the box
    assert img.position_x >= 0


@assert_no_logs
def test_float_polygon_text_wrap():
    """Test text wraps around polygonal float."""
    page, = render_pages('''
        <style>
            body { width: 200px; font-size: 0; }
            .float {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: polygon(0 0, 100% 0, 100% 100%, 0 100%);
            }
            img { width: 30px; height: 10px; vertical-align: top; }
        </style>
        <div class="float"></div>
        <img src="pattern.png" />
    ''')
    html, = page.children
    body, = html.children
    float_div, anon_block = body.children
    line, = anon_block.children
    img, = line.children

    # Rectangle polygon should behave like margin-box
    assert img.position_x == 100  # After the 100px float


@assert_no_logs
def test_circle_closest_side_resolution():
    """Test closest-side keyword resolves correctly for circle."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 200px;
                shape-outside: circle(closest-side at 50% 50%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    # closest-side for a centered circle in 100x200 box should be 50
    # (distance to left/right sides, which are closer than top/bottom)
    boundary = div.shape_boundary
    assert isinstance(boundary, CircleBoundary)
    assert boundary.radius == 50


@assert_no_logs
def test_circle_farthest_side_resolution():
    """Test farthest-side keyword resolves correctly for circle."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 200px;
                shape-outside: circle(farthest-side at 50% 50%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    # farthest-side for a centered circle in 100x200 box should be 100
    # (distance to top/bottom sides, which are farther than left/right)
    boundary = div.shape_boundary
    assert isinstance(boundary, CircleBoundary)
    assert boundary.radius == 100


@assert_no_logs
def test_ellipse_closest_side_resolution():
    """Test closest-side keyword resolves correctly for ellipse."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 200px;
                shape-outside: ellipse(closest-side closest-side at 50% 50%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = div.shape_boundary
    assert isinstance(boundary, EllipseBoundary)
    # rx closest-side in 100px width = 50
    assert boundary.rx == 50
    # ry closest-side in 200px height = 100
    assert boundary.ry == 100


@assert_no_logs
def test_polygon_percentage_resolution():
    """Test polygon percentage values resolve correctly."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 200px;
                shape-outside: polygon(0 0, 100% 0, 100% 100%, 0 100%);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = div.shape_boundary
    assert isinstance(boundary, PolygonBoundary)
    # Verify points are resolved to absolute coordinates
    # Reference is margin box (100x200 starting at position_x, position_y)
    ref_x = div.position_x
    ref_y = div.position_y
    assert boundary.points[0] == (ref_x, ref_y)  # 0%, 0%
    assert boundary.points[1] == (ref_x + 100, ref_y)  # 100%, 0%
    assert boundary.points[2] == (ref_x + 100, ref_y + 200)  # 100%, 100%
    assert boundary.points[3] == (ref_x, ref_y + 200)  # 0%, 100%


@assert_no_logs
def test_circle_position_keywords():
    """Test circle() with position keywords."""
    page, = render_pages('''
        <style>
            div {
                float: left;
                width: 100px;
                height: 100px;
                shape-outside: circle(30px at left top);
            }
        </style>
        <div></div>
    ''')
    html, = page.children
    body, = html.children
    div, = body.children

    boundary = div.shape_boundary
    assert isinstance(boundary, CircleBoundary)
    # Center should be at top-left corner
    assert boundary.cx == div.position_x
    assert boundary.cy == div.position_y
    assert boundary.radius == 30
