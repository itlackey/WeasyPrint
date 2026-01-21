"""CSS Shapes support for shape-outside property.

This module provides shape boundary classes for computing exclusion areas
around floated elements. Each boundary class implements the same interface
for querying shape bounds at specific Y coordinates.
"""

from abc import ABC, abstractmethod


class ShapeBoundary(ABC):
    """Abstract base class for shape-outside boundaries.

    Shape boundaries compute the horizontal exclusion range at any given
    Y coordinate within the shape's vertical extent.
    """

    @abstractmethod
    def get_bounds_at_y(self, y):
        """Get horizontal bounds of the shape at a specific Y coordinate.

        Args:
            y: The Y coordinate to query.

        Returns:
            tuple: (left_bound, right_bound) in absolute coordinates,
                   or None if the shape doesn't intersect at this Y.
        """
        pass

    @abstractmethod
    def get_vertical_extent(self):
        """Get the vertical range of the shape.

        Returns:
            tuple: (min_y, max_y) of the shape's vertical extent.
        """
        pass


class BoxBoundary(ShapeBoundary):
    """Rectangular boundary based on CSS box model.

    This boundary returns constant horizontal bounds regardless of Y position.
    For box-based shapes, the horizontal bounds don't vary with Y, so we always
    return the same bounds. The margin box is used for collision detection.
    """

    def __init__(self, box, box_type='margin-box'):
        """Initialize a box boundary.

        Args:
            box: The float box to compute bounds from.
            box_type: One of 'margin-box', 'border-box', 'padding-box',
                'content-box'.
        """
        self.box = box
        self.box_type = box_type
        self._compute_bounds()

    def _compute_bounds(self):
        """Precompute the box bounds.

        Computes horizontal bounds based on box_type for shape-outside,
        and vertical extent based on margin box for collision detection.
        """
        box = self.box
        # Horizontal bounds depend on the box_type (shape-outside value)
        if self.box_type == 'content-box':
            self.left = box.content_box_x()
            self.right = self.left + box.width
        elif self.box_type == 'padding-box':
            self.left = box.padding_box_x()
            self.right = self.left + box.padding_width()
        elif self.box_type == 'border-box':
            self.left = box.border_box_x()
            self.right = self.left + box.border_width()
        else:  # margin-box (default)
            self.left = box.position_x
            self.right = self.left + box.margin_width()

        # Vertical extent always uses margin box for collision detection
        # This matches the original behavior where collision detection
        # uses margin_height() but shape bounds use shape-outside value
        self.top = box.position_y
        self.bottom = self.top + box.margin_height()

    def get_bounds_at_y(self, y):
        """Get horizontal bounds at the given Y coordinate.

        For box-based shapes, horizontal bounds are constant regardless of Y.
        Since the collision detection in avoid_collisions() already checks
        for vertical overlap, we always return the bounds here. The collision
        detection handles cases where the shape overlaps with the box even if
        the query Y is outside the shape's vertical extent.
        """
        # For rectangular shapes, bounds are constant - always return them
        # The collision detection already verified there's vertical overlap
        return (self.left, self.right)

    def get_vertical_extent(self):
        """Get the vertical extent of the box (margin box)."""
        return (self.top, self.bottom)


def create_shape_boundary(box):
    """Create a shape boundary for a floated box.

    Args:
        box: The float box with shape_outside style.

    Returns:
        ShapeBoundary: A boundary object for computing shape exclusions.
    """
    shape_outside = box.style['shape_outside']

    if shape_outside in ('none', 'margin-box'):
        return BoxBoundary(box, 'margin-box')
    elif shape_outside == 'border-box':
        return BoxBoundary(box, 'border-box')
    elif shape_outside == 'padding-box':
        return BoxBoundary(box, 'padding-box')
    elif shape_outside == 'content-box':
        return BoxBoundary(box, 'content-box')

    # For future shape functions, we'll add handling here
    # For now, fall back to margin-box
    return BoxBoundary(box, 'margin-box')
