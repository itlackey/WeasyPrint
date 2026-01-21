"""Tests for CSS shape-outside property with box keyword values."""

import pytest

from weasyprint.layout.float import get_shape_box_bounds

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
    'circle(50%)',  # shape function (not yet supported)
    'ellipse(25% 50%)',  # shape function (not yet supported)
    'polygon(0 0, 100% 0, 100% 100%)',  # shape function (not yet supported)
    'url(image.png)',  # image reference (not yet supported)
    '50px',  # length value (invalid)
    '50%',  # percentage value (invalid)
    'auto',  # not a valid shape-outside value
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
