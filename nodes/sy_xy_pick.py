"""XY Pick SY: turns one running index into the X and Y value of one grid cell."""
try:
    from ._sy_common import category, register
    from ._sy_xy import axis_sizes, parse_axis, pick_cell
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_xy import axis_sizes, parse_axis, pick_cell


def pick(x_values, y_values, index, wrap=False):
    """Pure function. Returns (x_value, y_value, x_index, y_index, total). Row-major: x changes fastest."""
    xs, ys = parse_axis(x_values), parse_axis(y_values)
    nx, ny = axis_sizes(xs, ys)
    xi, yi = pick_cell(nx, ny, index, wrap)
    return (xs[xi] if xs else "", ys[yi] if ys else "", xi, yi, nx * ny)


def pick_ex(x_values, y_values, index, wrap=False, clamp=False):
    """Pure function. Like pick, plus a label and an is_last flag. clamp: an index past the end stays on the last cell.
    Returns (x_value, y_value, x_index, y_index, total, label, is_last)."""
    xs, ys = parse_axis(x_values), parse_axis(y_values)
    nx, ny = axis_sizes(xs, ys)
    total = nx * ny
    idx = int(index)
    if clamp and not wrap and idx >= total:
        idx = total - 1
    xv, yv, xi, yi, total = pick(x_values, y_values, idx, wrap)
    parts = []
    if xs:
        parts.append("X=" + xv)
    if ys:
        parts.append("Y=" + yv)
    cell = yi * nx + xi
    label = "cell %d of %d" % (cell + 1, total) + (": " + ", ".join(parts) if parts else "")
    return xv, yv, xi, yi, total, label, cell == total - 1


class SYXYPick:
    DESCRIPTION = ("Picks one cell of an XY grid from a running index. Feed it a counter and auto-queue to render the whole grid. "
                   "Also gives a plain label such as 'cell 2 of 6: X=b, Y=p' and a flag for the last cell. "
                   "Optionally stays on the last cell instead of stopping with an error.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "INT", "STRING", "BOOLEAN")
    RETURN_NAMES = ("x_value", "y_value", "x_index", "y_index", "total", "label", "is_last")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_values": ("STRING", {"default": "", "multiline": True, "tooltip": "The X list, one value per line. Empty means a single column."}),
                "y_values": ("STRING", {"default": "", "multiline": True, "tooltip": "The Y list, one value per line. Empty means a single row."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Cell number from 0, going across each row first."}),
                "wrap": ("BOOLEAN", {"default": False, "tooltip": "On: an index past the end starts again at 0. Off: it stops with an error."}),
            },
            "optional": {
                "clamp_to_last": ("BOOLEAN", {"default": False, "tooltip": "On: an index past the end stays on the last cell. Ignored when wrap is on."}),
            },
        }

    def run(self, x_values, y_values, index, wrap, clamp_to_last=False):
        return pick_ex(x_values, y_values, index, wrap, bool(clamp_to_last))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "XYPick", SYXYPick)
NODE_DISPLAY_NAME_MAPPINGS["SYXYPick"] = "XY Pick SY"
