"""Useful functions that largely conform to the matplotlib interface."""

from numbers import Real
from typing import Iterable, Optional

from matplotlib import pyplot


def axes_iter(iterable: Iterable, ncols: int = 3, width: Real = 13, row_height: Real = 4, sharey: bool = False,
              shared_ylabel: Optional[str] = None, clim_convex_hull: bool = False):
    """Iterate over the given iterable, but put a new set of axes on the context for each item.

    We automatically call tight_layout() after we have finished processing the iterable element.

    :param iterable: The elements over which to iterate.
    :param ncols: The number of columns in the grid.
    :param width: The total width of the resulting grid in matplotlib units.
    :param row_height: The height of each row in matplotlib units.
    :param sharey: If specified, each row will share y-axes.
    :param shared_ylabel: Iff sharey is true, and this is specified, set this as the common y-axis label.
    :param clim_convex_hull: Iff true, attempt to set the color scale limits to the convex hull of all internal color
        limits.
    """
    # All axes which have been yielded.
    all_axes = []

    # A temporary store of axes, from which we will yield.
    current_axes = []

    for item in iterable:
        if len(current_axes) == 0:
            # Need to create another row of axes.
            _, new_axes = pyplot.subplots(1, ncols, figsize=(width, row_height), sharey='row' if sharey else 'none')
            if sharey and shared_ylabel is not None:
                # We are sharing a y-axis, and want to set a common y-axis label. Set it here.
                pyplot.ylabel(shared_ylabel)
            if ncols == 1:
                # Have to work around matplotlib inconsistency here.
                current_axes = [new_axes]
            else:
                current_axes = list(new_axes)
        axes = current_axes.pop(0)
        pyplot.sca(axes)
        yield item
        all_axes.append(axes)
        pyplot.tight_layout()

    if clim_convex_hull:
        set_clim_to_convex_hull(*all_axes)


def set_clim_to_convex_hull(*all_axes):
    """Set the color scale limits of the given axes to the convex hull of all those specified."""
    min_limit = None
    max_limit = None

    # Save the current axes so we can restore the context after this function call.
    current_axes = pyplot.gca()

    for axes in all_axes:
        # This is the only public-API method for obtaining 'images' (e.g. a pcolormesh) from each axis.
        pyplot.sca(axes)
        image = pyplot.gci()
        this_min, this_max = image.get_clim()
        min_limit = this_min if min_limit is None else min(this_min, min_limit)
        max_limit = this_max if max_limit is None else max(this_max, max_limit)

    # We now have the new limits, so set everywhere.
    for axes in all_axes:
        pyplot.sca(axes)
        pyplot.clim(min_limit, max_limit)

    pyplot.sca(current_axes)
