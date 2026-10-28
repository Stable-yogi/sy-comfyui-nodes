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


class SYXYPick:
    DESCRIPTION = "Picks one cell of an XY grid from a running index. Feed it a counter and auto-queue to render the whole grid."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "INT")
    RETURN_NAMES = ("x_value", "y_value", "x_index", "y_index", "total")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "x_values": ("STRING", {"default": "", "multiline": True, "tooltip": "The X list, one value per line. Empty means a single column."}),
                "y_values": ("STRING", {"default": "", "multiline": True, "tooltip": "The Y list, one value per line. Empty means a single row."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 2 ** 31 - 1, "tooltip": "Cell number from 0, going across each row first."}),
                "wrap": ("BOOLEAN", {"default": False, "tooltip": "On: an index past the end starts again at 0. Off: it stops with an error."}),
            }
        }

    def run(self, x_values, y_values, index, wrap):
        return pick(x_values, y_values, index, wrap)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "XYPick", SYXYPick)
NODE_DISPLAY_NAME_MAPPINGS["SYXYPick"] = "XY Pick SY"
